from uasyncio import get_event_loop, sleep_ms
from machine import reset, Pin, SPI
from time import sleep
from gc import collect, mem_free
from network import WLAN, STA_IF, AP_IF
from re import match
from max7219 import Matrix8x8
from connectivity_manager import ConnectivityManager
from settings import Settings
from credentials import Credentials
from tags import Tags
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

CHECK_CONNECTED = const(250) # milliseconds
WAIT_BEFORE_RESET = const(10) # seconds
MQTT_CHECK_MESSAGE_INTERVAL = const(250) # milliseconds
MQTT_CHECK_CONNECTED_INTERVAL = const(1000) # milliseconds

class State:
    OFF = 0
    ON = 1

    STATE_TEXT = ["OFF", "ON"]

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
        # print("> ### CONNECTIVITY UP ###")
        # collect()
        # print("> Free mem: {}".format(mem_free()))

        self.display.get_time = self.connectivity.get_time
        self.display.ip = self.connectivity.get_ip()

        settings = Settings().load()

        if settings.state != b"%s" % State.ON:
            self.display.off()
        else:
            self.display.display_clock()

        self.set_state()

    def connectivity_down(self):
        self.display.display_spinner()

    def on_off(self, topic, message):
        print("> ### {:s} / {:s}".format(topic, message))
        # if match("on", message):
        #     self.display.display_clock()
        #     settings.state = b"%s" % State.ON
        #     settings.write()
        #     self.set_state()
        # elif match("off", message):
        #     self.display.off()
        #     settings.state = b"%s" % State.OFF
        #     settings.write()
        #     self.set_state()

    async def check_connected(self):
        while True:
            while not self.sta_if.isconnected() or self.ap_if.active():
                await sleep_ms(CHECK_CONNECTED)

            settings = Settings().load()

            if settings.state != b"%s" % State.ON:
                self.clock.stop()
            else:
                self.clock.start()

            self.set_state()

            while self.sta_if.isconnected():
                await sleep_ms(CHECK_CONNECTED)

    def check_message_mqtt(self):
        settings = Settings().load()

        try:
            mqtt_message = self.mqtt.check_messages()
            tags = Tags().load()

            if mqtt_message:
                topic = mqtt_message.get(b"topic")
                message = mqtt_message.get(b"message")

                print("> MQTT message received: %s / %s" % (topic, message))
                
                elif match("on", message):
                    self.clock.start()
                    settings.state = b"%s" % State.ON
                    settings.write()
                    self.set_state()
                elif match("off", message):
                    self.clock.stop()
                    settings.state = b"%s" % State.OFF
                    settings.write()
                    self.set_state()

        except Exception as e:
            print("> Main.check_message_mqtt exception: {}".format(e))

    def settings_values(self, params):
        settings = Settings().load()

        if settings.state == b"%s" % State.OFF:
            brightness = 0
        else:
            brightness = int(settings.brightness)

        result = (
            b'{"ip": "%s", "netId": "%s", "brightness": "%s"}'
            % (self.wifi.ip, settings.net_id, brightness)
        )

        return result

    def set_brightness(self, params):
        settings = Settings().load()
        l = int(params.get(b"l", 0))

        if l == 0:
            settings.state = b"%s" % State.OFF
            self.clock.stop()
        elif l < 12:
            settings.state = b"%s" % State.ON
            settings.brightness = b"%s" % l

            self.board.brightness(l-1)
            self.clock.start()

        settings.write()
        self.set_state()

    def set_state(self):
        settings = Settings().load()
        self.mqtt.set_state(State.STATE_TEXT[int(settings.state)])

try:
    collect()
    print("\n> >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print("> Free mem after all classes created: {}".format(mem_free()))
    print("> >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n")

    main = Main()

except Exception as e:
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))
    sleep(WAIT_BEFORE_RESET)
    reset()
