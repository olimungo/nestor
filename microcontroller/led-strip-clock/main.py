from uasyncio import get_event_loop, sleep_ms
from machine import reset
from gc import collect, mem_free
from network import WLAN, STA_IF, AP_IF
from re import match

from WifiManager import WifiManager
from HttpServer import HttpServer
from mDnsServer import mDnsServer
from MqttManager import MqttManager
from Clock import Clock
from Spinner import Spinner
from Settings import Settings
from Credentials import Credentials
from Tags import Tags

PUBLIC_NAME = b"Clock"
BROKER_NAME = b"nestor.local"
# BROKER_NAME = b"192.168.0.215"
MQTT_TOPIC_NAME = b"clocks"
DEVICE_TYPE = b"CLOCK"

ORANGE = (255, 98, 0)
GREEN = (19, 215, 19)
SPINNER_RATE = const(120)
SPINNER_MINIMUM_DISPLAY = const(2000)

CHECK_CONNECTED = const(250)
WAIT_BEFORE_RESET = const(10000)
MQTT_CHECK_MESSAGE_INTERVAL = const(250)
MQTT_CHECK_CONNECTED_INTERVAL = const(1000)

class State:
    CLOCK = 0
    OFF = 1

    STATE_TEXT = ["CLOCK", "OFF"]

class Main:
    def __init__(self):
        self.sta_if = WLAN(STA_IF)
        self.ap_if = WLAN(AP_IF)
        settings = Settings(state=b"%s" % State.CLOCK).load()

        self.wifi = WifiManager(b"%s-%s" % (PUBLIC_NAME, settings.net_id))
        self.mdns = mDnsServer(PUBLIC_NAME.lower(), settings.net_id)
        self.mqtt = MqttManager(
            self.mdns, BROKER_NAME, settings.net_id, MQTT_TOPIC_NAME, DEVICE_TYPE
        )

        routes = {
            b"/action/color": self.set_color,
            b"/action/clock/display": self.display_clock,
            b"/action/brightness": self.set_brightness,
            b"/settings/values": self.settings_values,
        }

        self.http = HttpServer(routes, self.wifi, self.mdns)

        self.clock = Clock(self.wifi, settings.color)
        self.spinner = Spinner()

        self.loop = get_event_loop()
        self.loop.create_task(self.check_connected())
        self.loop.create_task(self.check_mqtt())
        self.loop.run_forever()
        self.loop.close()

    async def check_connected(self):
        while True:
            self.clock.stop()

            credentials = Credentials().load()

            if credentials.is_valid() and credentials.essid != b"" and credentials.password != b"":
                color = GREEN
            else:
                color = ORANGE

            self.spinner.start(SPINNER_RATE, color)

            # Spin at least for 2 seconds
            await sleep_ms(SPINNER_MINIMUM_DISPLAY)

            while not self.sta_if.isconnected() or self.ap_if.active():
                await sleep_ms(CHECK_CONNECTED)

            self.spinner.stop()

            settings = Settings().load()

            if settings.state != b"%s" % State.OFF:
                settings.state = b"%s" % State.CLOCK
                settings.write()
                self.clock.start()
            else:
                self.clock.clear_all()

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

        if settings.state == b"%s" % State.OFF:
                l = 0
        else:
            _, _, l = self.clock.hsl

        result = (
            b'{"ip": "%s", "netId": "%s",  "essid": "%s", "brightness": "%s"}'
            % (self.wifi.ip, settings.net_id, essid, int(l))
        )

        return result

    def display_clock(self, params=None):
        settings = Settings().load()

        if settings.state != b"%s" % State.CLOCK:
            settings.state = b"%s" % State.CLOCK
            settings.write()
            self.clock.start()

            self.set_state()

    def set_color(self, params):
        settings = Settings().load()

        self.display_clock()

        color = params.get(b"hex", None)

        if color:
            self.clock.set_color(color)

            settings.color = color
            settings.write()

        _, _, l = self.clock.hsl

        settings.state = b"%s" % State.CLOCK
        settings.write()

        return b'{"brightness": "%s"}' % int(l)

    def set_brightness(self, params):
        settings = Settings().load()

        l = int(params.get(b"l", 0))

        if l > 0:
            self.display_clock()
            self.clock.set_brightness(l)

            settings.color = b"%s" % self.clock.hex
            settings.state = b"%s" % State.CLOCK
        else:
            self.clock.off()
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
    sleep_ms(WAIT_BEFORE_RESET)
    reset()
