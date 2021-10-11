from uasyncio import get_event_loop, sleep_ms
from machine import reset
from time import sleep
from gc import collect, mem_free
from network import WLAN, STA_IF, AP_IF
from re import match
from wifi_manager import WifiManager
from http_server import HttpServer
from mdns_server import mDnsServer
from mqtt_manager import MqttManager
from settings import Settings
from tags import Tags
from display import Display

DEVICE_TYPE = b"CLOCK"
PUBLIC_NAME = b"Clock"
BROKER_NAME = b"nestor.local"
# BROKER_NAME = b"deathstar.local"
MQTT_TOPIC_NAME = b"clocks"
CHECK_CONNECTED = const(250)
WAIT_BEFORE_RESET = const(10)
MQTT_CHECK_MESSAGE_INTERVAL = const(250)
MQTT_CHECK_CONNECTED_INTERVAL = const(1000)
SPINNER_MINIMUM_DISPLAY = const(2000)

class State:
    OFF = 0
    CLOCK = 1

    STATE_TEXT = ["OFF", "CLOCK"]

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
            b"/action/color": self.set_color,
            b"/action/clock/display": self.display_clock,
            b"/action/brightness": self.set_brightness,
            b"/settings/values": self.settings_values,
        }

        self.http = HttpServer(routes, self.wifi, self.mdns)

        self.display = Display(self.wifi)

        self.loop = get_event_loop()
        self.loop.create_task(self.check_connected())
        self.loop.create_task(self.check_mqtt())
        self.loop.run_forever()
        self.loop.close()

    async def check_connected(self):
        while True:
            self.display.display_spinner()

            # Spin at least for 2 seconds
            await sleep_ms(SPINNER_MINIMUM_DISPLAY)

            while not self.sta_if.isconnected() or self.ap_if.active():
                await sleep_ms(CHECK_CONNECTED)

            settings = Settings().load()

            if settings.state != b"%s" % State.CLOCK:
                self.display.off()
            else:
                self.display.display_clock()

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
        settings = Settings().load()

        if settings.state == b"%s" % State.OFF:
            l = 0
        else:
            _, _, l = self.display.clock.hsl

        result = (
            b'{"ip": "%s", "netId": "%s",  "brightness": "%s", "color": "%s"}'
            % (self.wifi.ip, settings.net_id, int(l), settings.color.decode('ascii'))
        )

        return result

    def display_clock(self, params=None):
        settings = Settings().load()

        if settings.state != b"%s" % State.CLOCK:
            settings.state = b"%s" % State.CLOCK
            settings.write()
            self.display.display_clock()
            self.set_state()

    def set_color(self, params):
        settings = Settings().load()

        self.display_clock()

        color = params.get(b"hex", None)

        if color:
            self.display.clock.set_color(color)

            settings.color = color
            settings.write()

        _, _, l = self.display.clock.hsl

        settings.state = b"%s" % State.CLOCK
        settings.write()

        return b'{"brightness": "%s"}' % int(l)

    def set_brightness(self, params):
        settings = Settings().load()

        l = int(params.get(b"l", 0))

        if l > 0:
            self.display_clock()
            self.display.clock.set_brightness(l)

            settings.color = b"%s" % self.display.clock.hex
            settings.state = b"%s" % State.CLOCK
        else:
            self.display.off()
            settings.state = b"%s" % State.OFF
            self.set_state()

        settings.write()

    def set_state(self):
        settings = Settings().load()
        self.mqtt.set_state(State.STATE_TEXT[int(settings.state)])

try:
    collect()
    print("Free mem: {}".format(mem_free()))

    main = Main()
except Exception as e:
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))
    sleep(WAIT_BEFORE_RESET)
    reset()
