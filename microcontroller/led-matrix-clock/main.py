from uasyncio import get_event_loop, sleep_ms
from machine import reset, Pin, SPI
from gc import collect, mem_free
from network import WLAN, STA_IF, AP_IF
from re import match
from max7219 import Matrix8x8
from wifi_manager import WifiManager
from http_server import HttpServer
from mdns_server import mDnsServer
from mqtt_manager import MqttManager
from settings import Settings
from credentials import Credentials
from tags import Tags
from clock import Clock

PUBLIC_NAME = b"Clock"
BROKER_NAME = b"nestor.local"
# BROKER_NAME = b"deathstar.local"
MQTT_TOPIC_NAME = b"clocks"
DEVICE_TYPE = b"CLOCK"
SPINNER_MINIMUM_DISPLAY = const(2000)
CS = const(15)

CHECK_CONNECTED = const(250)
WAIT_BEFORE_RESET = const(10000)
MQTT_CHECK_MESSAGE_INTERVAL = const(250)
MQTT_CHECK_CONNECTED_INTERVAL = const(1000)

class Main:
    def __init__(self):
        self.sta_if = WLAN(STA_IF)
        self.ap_if = WLAN(AP_IF)
        settings = Settings().load()

        self.wifi = WifiManager(b"%s-%s" % (PUBLIC_NAME, settings.net_id))
        self.mdns = mDnsServer(PUBLIC_NAME.lower(), settings.net_id)
        self.mqtt = MqttManager(
            self.mdns, BROKER_NAME, settings.net_id, MQTT_TOPIC_NAME, DEVICE_TYPE
        )

        routes = {
            b"/action/brightness": self.set_brightness,
            b"/settings/values": self.settings_values,
        }

        self.http = HttpServer(routes, self.wifi, self.mdns)

        self.spi = SPI(1, baudrate=10000000, polarity=1, phase=0)
        self.board = Matrix8x8(self.spi, Pin(CS), 4)
        self.board.brightness(int(settings.brightness))
        self.board.fill(0)
        self.board.show()

        self.clock = Clock(self.board)

        self.loop = get_event_loop()
        self.loop.create_task(self.check_connected())
        self.loop.create_task(self.check_mqtt())
        self.loop.run_forever()
        self.loop.close()

    async def check_connected(self):
        while True:
            while not self.sta_if.isconnected() or self.ap_if.active():
                await sleep_ms(CHECK_CONNECTED)

            self.set_state()

            settings = Settings().load()
            
            if settings.brightness != b"0":
                self.clock.start()

            while self.sta_if.isconnected():
                await sleep_ms(CHECK_CONNECTED)

    async def check_mqtt(self):
        while True:
            while self.mqtt.connected:
                self.check_message_mqtt()

                await sleep_ms(MQTT_CHECK_MESSAGE_INTERVAL)

            while not self.mqtt.connected:
                await sleep_ms(MQTT_CHECK_CONNECTED_INTERVAL)

            self.set_state()

    def check_message_mqtt(self):
        try:
            message = self.mqtt.check_messages()
            tags = Tags().load()

            if message:
                if match("add-tag/", message):
                    tag = message.split(b"/")[1]
                    tags.append(tag)
                elif match("remove-tag/", message):
                    tag = message.split(b"/")[1]
                    tags.remove(tag)

        except Exception as e:
            print("> Main.check_message_mqtt exception: {}".format(e))

    def settings_values(self, params):
        credentials = Credentials().load()
        settings = Settings().load()

        essid = credentials.essid

        if not essid:
            essid = b""

        result = (
            b'{"ip": "%s", "netId": "%s",  "essid": "%s", "brightness": "%s"}'
            % (self.wifi.ip, settings.net_id, essid, int(settings.brightness))
        )

        return result

    def set_brightness(self, params):
        settings = Settings().load()
        l = int(params.get(b"l", 0))

        if l >= 0 or l < 12:
            settings.brightness = b"%s" % l
            settings.write()

            if l == 0:
                self.clock.stop()
            else:
                self.board.brightness(l-1)
                self.clock.start()

            self.set_state()

    def set_state(self):
        settings = Settings().load()

        if settings.brightness == b"0":
            state = "OFF"
        else:
            state = "ON"

        self.mqtt.set_state(state)

try:
    collect()
    print("Free mem: {}".format(mem_free()))

    main = Main()
except Exception as e:
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))
    sleep_ms(WAIT_BEFORE_RESET)
    reset()
