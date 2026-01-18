from uasyncio import get_event_loop, sleep_ms
from machine import reset, Pin
from time import sleep, ticks_ms, ticks_diff
from gc import collect, mem_free
from re import match
from math import floor
from connectivity_manager import ConnectivityManager
from settings import Settings

PUBLIC_NAME = b"Remote"
BROKER_NAME = b"nestor.local"
# BROKER_NAME = b"death-star.local"
MQTT_TOPIC_NAME = b"remotes"
DEVICE_TYPE = b"REMOTE"

DEBOUNCE_BUTTON = const(500) # milliseconds
WAIT_FOR_BUTTON_PRESSED = const(100) # milliseconds
WAIT_BEFORE_RESET = const(3) # seconds

USE_MDNS = True
USE_MQTT = True
USE_NTP = False

PIN_BUTTON_A = const(14)  # D5 - GPIO14
PIN_BUTTON_B = const(12)  # D6 - GPIO12

class Main:
    button_a_state = False
    button_b_state = False

    def __init__(self):
        url_routes = {
            b"/action/command": self.define_command,
        }

        mqtt_subscribe_topics = {}

        self.connectivity = ConnectivityManager(PUBLIC_NAME, BROKER_NAME, url_routes,
            MQTT_TOPIC_NAME, mqtt_subscribe_topics, DEVICE_TYPE,
            self.connectivity_up, self.connectivity_down,
            use_ntp=USE_NTP, use_mdns=USE_MDNS, use_mqtt=USE_MQTT)

        self.set_state()

        self.button_a = Pin(PIN_BUTTON_A, Pin.IN, Pin.PULL_UP)
        self.button_b = Pin(PIN_BUTTON_B, Pin.IN, Pin.PULL_UP)

        self.loop = get_event_loop()

        self.loop.create_task(self.check_buttons())

        self.loop.run_forever()
        self.loop.close()

    async def check_buttons(self):
        button_a_active = 0
        button_b_active = 0

        while True:
            button_a_active = self.debounce_button(button_a_active)
            button_b_active = self.debounce_button(button_b_active)
            settings = Settings().load()

            if self.button_a.value() == 0 and button_a_active == 0:
                button_a_active = ticks_ms()
                self.button_a_state = self.set_new_state(settings.command_a, self.button_a_state)
            
            if self.button_b.value() == 0 and button_b_active == 0:
                button_b_active = ticks_ms()
                self.button_b_state = self.set_new_state(settings.command_b, self.button_b_state)

            await sleep_ms(WAIT_FOR_BUTTON_PRESSED)

    def set_new_state(self, command, button_state):
        if command.find(b":") != -1:
            self.process_command(command)
        else:
            if button_state:
                command =  command + b":off"
            else:
                command =  command + b":on"

            self.process_command(command)

            return not button_state

    def debounce_button(self, button_active):
        if button_active != 0:
            now = ticks_ms()

            if ticks_diff(now, button_active) > DEBOUNCE_BUTTON:
                button_active = 0

        return button_active

    def process_command(self, commands):
        for command in commands.split(b";"):
            tokens = command.split(b":")
            self.publish_command(tokens[0], tokens[1])

    def connectivity_up(self):
        collect()
        print("> Free mem after all services up: {}".format(mem_free()))

    def connectivity_down(self):
        pass

    def define_command(self, path, params):
        button = params.get(b"button", None)
        command = params.get(b"command", None)

        settings = Settings().load()

        if button == b"a":
            settings.command_a = command
        else:
            settings.command_b = command

        settings.write()

        self.set_state()

    def publish_command(self,  device, message):
        print("> MQTT command to be sent: {} / {} ".format(device, message))

        self.connectivity.publish_mqtt_message(device, message)

    def set_state(self):
        settings = Settings().load()

        http_config = {b"commandA": settings.command_a, b"commandB": settings.command_b}

        self.connectivity.set_state(http_config, b"ACTIVE")
try:
    Main()
except Exception as e:
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))
    sleep(WAIT_BEFORE_RESET)
    reset()
