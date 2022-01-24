from uasyncio import get_event_loop, sleep_ms
from machine import reset, Pin, SPI
from time import sleep
from gc import collect, mem_free
from max7219 import Matrix8x8
from connectivity_manager import ConnectivityManager
from settings import Settings
from clock import Clock

PUBLIC_NAME = b"Clock"
BROKER_NAME = b"nestor.local"
# BROKER_NAME = b"death-star.local"
MQTT_TOPIC_NAME = b"clocks"
MQTT_DEVICE_TYPE = b"CLOCK"
HTTP_DEVICE_TYPE = b"CLOCK"

SEND_STATE_INTERVAL = const(2000)
WAIT_BEFORE_RESET = const(10) # seconds
SPINNER_MINIMUM_DISPLAY = const(2000)

CS = const(15)

class Main:
    def __init__(self):
        settings = Settings().load()

        url_routes = {
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

        self.spi = SPI(1, baudrate=10000000, polarity=1, phase=0)
        self.board = Matrix8x8(self.spi, Pin(CS), 4)

        self.board.brightness(int(settings.brightness))
        self.board.fill(0)
        self.board.show()

        self.clock = Clock(self.board)

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

        self.clock.get_time = self.connectivity.get_time

        settings = Settings().load()

        if settings.state != b"1":
            self.clock.stop()
        else:
            self.clock.start()

        self.set_state()

    def connectivity_down(self):
        # TODO: display something so to know the connectivity is down
        pass

    def on_off(self, topic, message):
        settings = Settings().load()

        if message == b"on" or message == b"off":
            if message == b"on":
                self.clock.start()
                settings.state = b"1"
            elif message == b"off":
                self.clock.stop()
                settings.state = b"0"

            settings.write()
            self.set_state()

    def set_brightness(self, path, params):
        settings = Settings().load()
        l = int(params.get(b"l", 0))

        if l == 0:
            settings.state = b"0"
            self.clock.stop()
        elif l < 12:
            settings.state = b"1"
            settings.brightness = b"%s" % l

            self.board.brightness(l-1)
            self.clock.start()

        settings.write()
        self.set_state()

    def set_state(self):
        settings = Settings().load()

        if settings.state == b"0":
            brightness = b"0"
            state = b"OFF"
        else:
            brightness = settings.brightness
            state = b"ON"

        http_config = {b"brightness": brightness}

        self.connectivity.set_state(http_config, state)

try:
    main = Main()
except Exception as e:
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))
    sleep(WAIT_BEFORE_RESET)
    reset()
