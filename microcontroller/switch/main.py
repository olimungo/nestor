from uasyncio import get_event_loop, sleep_ms
from machine import reset, Pin
from gc import collect, mem_free
from network import WLAN, STA_IF, AP_IF
from re import match
from wifi_manager import WifiManager
from http_server import HttpServer
from mdns_server import mDnsServer
from mqtt_manager import MqttManager
from settings import Settings
from credentials import Credentials
from tags import Tags

PUBLIC_NAME = b"Switch"
# BROKER_NAME = b"nestor.local"
BROKER_NAME = b"deathstar.local"
MQTT_TOPIC_NAME = b"switches"
DEVICE_TYPE = b"SWITCH"

CHECK_CONNECTED = const(250)
WAIT_BEFORE_RESET = const(10000)
MQTT_CHECK_MESSAGE_INTERVAL = const(250)
MQTT_CHECK_CONNECTED_INTERVAL = const(1000)

PIN_SWITCH = const(5)  # D1

class Main:
    def __init__(self):
        self.sta_if = WLAN(STA_IF)
        self.ap_if = WLAN(AP_IF)
        settings = Settings().load()

        self.wifi = WifiManager(b"%s-%s" % (PUBLIC_NAME, settings.net_id))
        self.mdns = mDnsServer(PUBLIC_NAME.lower(), settings.net_id)
        self.mqtt = MqttManager(
            self.mdns, BROKER_NAME, MQTT_TOPIC_NAME, DEVICE_TYPE
        )

        routes = {
            b"/action/toggle": self.toggle,
            b"/settings/values": self.settings_values
        }

        self.http = HttpServer(routes, self.wifi, self.mdns)

        self.switch = Pin(PIN_SWITCH, Pin.OUT)

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
            b'{"ip": "%s", "netId": "%s",  "essid": "%s", "state": "%s"}'
            % (self.wifi.ip, settings.net_id, essid, settings.state,)
        )

        return result

    def toggle(self, params):
        action = params.get(b"action", None)
        settings = Settings().load()

        if action == b"on":
            self.switch.on()
            settings.state = b"1"
        else:
            self.switch.off()
            settings.state = b"0"

        settings.write()

    def set_state(self):
        settings = Settings().load()

        if settings.state == b"1":
            state = "ON"
        else:
            state = "OFF"

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
