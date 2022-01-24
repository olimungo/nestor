from uasyncio import get_event_loop, sleep_ms
from machine import reset
from time import sleep
from gc import collect, mem_free
from connectivity_manager import ConnectivityManager
from settings import Settings
from display import Display

PUBLIC_NAME = b"Clock"
BROKER_NAME = b"nestor.local"
# BROKER_NAME = b"death-star.local"
MQTT_TOPIC_NAME = b"clocks"
MQTT_DEVICE_TYPE = b"CLOCK"
HTTP_DEVICE_TYPE = b"CLOCK"

SEND_STATE_INTERVAL = const(2000)
WAIT_BEFORE_RESET = const(10) # seconds

class Main:
    def __init__(self):
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
            MQTT_TOPIC_NAME, mqtt_subscribe_topics,
            MQTT_DEVICE_TYPE, HTTP_DEVICE_TYPE,
            self.connectivity_up, self.connectivity_down,
            use_ntp=True, use_mdns=True, use_mqtt=True)

        self.display = Display(self.connectivity.get_ip())
        self.display.display_spinner()

        self.set_state()

        self.loop = get_event_loop()
        self.loop.create_task(self.send_state())
        self.loop.run_forever()
        self.loop.close()

    async def send_state(self):
        while True:
            self.set_state()
            await sleep_ms(SEND_STATE_INTERVAL)

    def connectivity_up(self):
        collect()
        print("> Free mem after all services up: {}".format(mem_free()))

        self.display.get_time = self.connectivity.get_time
        self.display.ip = self.connectivity.get_ip()

        settings = Settings().load()

        if settings.state != b"1":
            self.display.off()
        else:
            self.display.display_clock()

        self.set_state()

    def connectivity_down(self):
        self.display.display_spinner()

    def on_off(self, topic, message):
        settings = Settings().load()

        if message == b"on" or message == b"off":
            if message == b"on":
                self.display.display_clock()
                settings.state = b"1"
            elif message == b"off":
                self.display.off()
                settings.state = b"0"

            settings.write()
            self.set_state()
        
    def display_clock(self, path=None, params=None):
        settings = Settings().load()

        if settings.state != b"1":
            settings.state = b"1"
            settings.write()
            self.display.display_clock()
            self.set_state()

    def set_color(self, path, params):
        settings = Settings().load()

        self.display_clock()

        color = params.get(b"hex", None)

        if color:
            self.display.clock.set_color(color)

            settings.color = color
            settings.write()

        _, _, l = self.display.clock.hsl

        settings.state = b"1"
        settings.write()

        return b'{"brightness": "%s"}' % int(l)

    def set_brightness(self, path, params):
        settings = Settings().load()

        l = int(params.get(b"l", 0))

        if l > 0:
            self.display_clock()
            self.display.clock.set_brightness(l)

            settings.color = b"%s" % self.display.clock.hex
            settings.state = b"1"
        else:
            self.display.off()
            settings.state = b"0"

        settings.write()
        self.set_state()

    def set_state(self):
        settings = Settings().load()

        if settings.state == b"0":
            l = 0
            state = b"OFF"
        else:
            _, _, l = self.display.clock.hsl
            state = b"ON"

        http_config = {b"brightness": b"%s" % l, b"color": settings.color}

        self.connectivity.set_state(http_config, state)

try:
    main = Main()
except Exception as e:
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))
    sleep(WAIT_BEFORE_RESET)
    reset()
