from uasyncio import get_event_loop
from machine import reset
from time import sleep
from gc import collect, mem_free
from connectivity_manager import ConnectivityManager
from settings import Settings
from clock import Clock
from blink import Blink
from clock_version import get_version, get_version_date

PUBLIC_NAME = b"Clock"
BROKER_NAME = b"nestor.local"
# BROKER_NAME = b"death-star.local"
MQTT_TOPIC_NAME = b"clocks"
DEVICE_TYPE = b"CLOCK"

WAIT_BEFORE_RESET = const(3) # seconds

USE_MDNS = True
USE_MQTT = True
CLOCK_SIZE = b"LARGE" # LARGE or SMALL

class Main:
    def __init__(self):
        print("> >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print("> LED Strip Clock: {} ({})".format(get_version(), get_version_date()))
        print("> >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")

        url_routes = {
            b"/action/color": self.set_color,
            b"/action/clock/display": self.display_clock,
            b"/action/brightness": self.set_brightness
        }

        mqtt_subscribe_topics = {
            b"on": self.on_off,
            b"off": self.on_off
        }

        self.connectivity = ConnectivityManager(PUBLIC_NAME, BROKER_NAME, url_routes,
            MQTT_TOPIC_NAME, mqtt_subscribe_topics, DEVICE_TYPE,
            self.connectivity_up, self.connectivity_down,
            use_ntp=True, use_mdns=USE_MDNS, use_mqtt=USE_MQTT)

        self.clock = Clock(self.connectivity.get_ip, self.connectivity.get_time, Settings().load().color, CLOCK_SIZE)
        self.clock.spinner_on()

        self.set_state()

        self.loop = get_event_loop()
        self.loop.run_forever()
        self.loop.close()

    def connectivity_up(self):
        settings = Settings().load()

        if settings.state != b"1":
            self.clock.off()
        else:
            self.clock.on()

        self.set_state()

        collect()
        print("> Free mem after all services up: {}".format(mem_free()))

    def connectivity_down(self):
        self.clock.spinner_on()

    def on_off(self, topic, message):
        settings = Settings().load()

        if message == b"on" or message == b"off":
            if message == b"on":
                self.clock.on()
                settings.state = b"1"
            elif message == b"off":
                self.clock.off()
                settings.state = b"0"

            settings.write()
            self.set_state()

    def display_clock(self, path=None, params=None):
        settings = Settings().load()

        if settings.state != b"1":
            settings.state = b"1"
            settings.write()
            self.clock.on()
            self.set_state()

    def set_color(self, path, params):
        settings = Settings().load()

        self.display_clock()

        color = params.get(b"hex", None)

        if color:
            self.clock.set_color(color)

            settings.color = color
            settings.write()

        _, _, l = self.clock.hsl

        settings.state = b"1"
        settings.write()

        return b'{"brightness": "%s"}' % int(l)

    def set_brightness(self, path, params):
        settings = Settings().load()

        l = int(params.get(b"l", 0))

        if l > 0:
            self.display_clock()
            self.clock.set_brightness(l)

            settings.color = b"%s" % self.clock.hex
            settings.state = b"1"
        else:
            self.clock.off()
            settings.state = b"0"

        settings.write()
        self.set_state()

    def set_state(self):
        settings = Settings().load()

        if settings.state == b"0":
            l = 0
            state = b"OFF"
        else:
            _, _, l = self.clock.hsl
            state = b"ON"

        http_config = {b"brightness": b"%s" % l, b"color": settings.color}

        self.connectivity.set_state(http_config, state)

try:
    Main()
except Exception as e:
    Blink().flash_once_slow()
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))

    sleep(WAIT_BEFORE_RESET)
    reset()
