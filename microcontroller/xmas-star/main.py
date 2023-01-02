from uasyncio import get_event_loop, sleep_ms
from machine import reset, Pin
from time import sleep, ticks_ms, ticks_diff
from gc import collect, mem_free
# from connectivity_manager import ConnectivityManager
from settings import Settings
from display import Display

PUBLIC_NAME = b"Xmas-Star"
BROKER_NAME = b"nestor.local"
# BROKER_NAME = b"death-star.local"
MQTT_TOPIC_NAME = b"xmas-stars"
DEVICE_TYPE = b"XMAS-STAR"

DEBOUNCE_BUTTON = const(250) # milliseconds
WAIT_FOR_BUTTON_PRESSED = const(100) # milliseconds
WAIT_BEFORE_RESET = const(10) # seconds

USE_MDNS = False
USE_MQTT = False
USE_NTP = False

PIN_BUTTON = const(4)  # D2 - GPIO4

class Main:
    def __init__(self):
        self.button = Pin(PIN_BUTTON, Pin.IN, Pin.PULL_UP)
        self.display = Display()

        self.loop = get_event_loop()

        # self.loop.create_task(self.setup())
        self.loop.create_task(self.check_button())

        self.loop.run_forever()
        self.loop.close()

    # async def setup(self):
    #     url_routes = {
    #         # b"/action/command": self.define_command,
    #     }

    #     mqtt_subscribe_topics = {}

    #     self.connectivity = ConnectivityManager(PUBLIC_NAME, BROKER_NAME, url_routes,
    #         MQTT_TOPIC_NAME, mqtt_subscribe_topics, DEVICE_TYPE,
    #         self.connectivity_up, self.connectivity_down,
    #         use_ntp=USE_NTP, use_mdns=USE_MDNS, use_mqtt=USE_MQTT)

    #     self.set_state()

    async def check_button(self):
        button_active = 0

        while True:
            button_active = self.debounce_button(button_active)

            if self.button.value() == 0 and button_active == 0:
                button_active = ticks_ms()

                self.display.next_mode()
            
            await sleep_ms(WAIT_FOR_BUTTON_PRESSED)

    def debounce_button(self, buttonctive):
        if buttonctive != 0:
            now = ticks_ms()

            if ticks_diff(now, buttonctive) > DEBOUNCE_BUTTON:
                buttonctive = 0

        return buttonctive

    def connectivity_up(self):
        collect()
        print("> Free mem after all services up: {}".format(mem_free()))

    def connectivity_down(self):
        pass

    def publish_command(self,  device, message):
        print("> MQTT command to be sent: {} / {} ".format(device, message))

        self.connectivity.publish_mqtt_message(device, message)

    def set_state(self):
        settings = Settings().load()

        http_config = {b"command": settings.mode}

        self.connectivity.set_state(http_config, b"ACTIVE")
try:
    Main()
except Exception as e:
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))
    sleep(WAIT_BEFORE_RESET)
    reset()
