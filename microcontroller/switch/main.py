from uasyncio import get_event_loop, sleep_ms
from machine import reset, Pin
from time import sleep
from gc import collect, mem_free
from re import match
from connectivity_manager import ConnectivityManager
from settings import Settings

PUBLIC_NAME = b"Switch"
BROKER_NAME = b"nestor.local"
# BROKER_NAME = b"death-star.local"
MQTT_TOPIC_NAME = b"switches"
MQTT_DEVICE_TYPE = b"SWITCH"
# HTTP_DEVICE_TYPE = b"SWITCH"
HTTP_DEVICE_TYPE = b"DOUBLE-SWITCH"

SEND_STATE_INTERVAL = const(2000)
WAIT_BEFORE_RESET = const(10) # seconds

PIN_SWITCH_A = const(5)  # D1
PIN_SWITCH_B = const(4)  # D2

class Main:
    def __init__(self):

        settings = Settings().load()

        url_routes = {
            b"/action/toggle-a": self.toggle_a_b,
            b"/action/toggle-b": self.toggle_a_b
        }

        mqtt_subscribe_topics = {
            b"on": self.on_off,
            b"of": self.on_off
        }

        self.connectivity = ConnectivityManager(PUBLIC_NAME, BROKER_NAME, url_routes,
            MQTT_TOPIC_NAME, mqtt_subscribe_topics,
            MQTT_DEVICE_TYPE, HTTP_DEVICE_TYPE,
            use_ntp=True, use_mdns=True, use_mqtt=True)

        self.set_state()

        self.switch_a = Pin(PIN_SWITCH_A, Pin.OUT)
        self.switch_b = Pin(PIN_SWITCH_B, Pin.OUT)

        self.switch_a.on() if settings.state_a == b"1" else self.switch_a.off()
        self.switch_b.on() if settings.state_b == b"1" else self.switch_b.off()

        self.loop = get_event_loop()
        self.loop.create_task(self.send_state())
        self.loop.run_forever()
        self.loop.close()

    async def send_state(self):
        while True:
            self.set_state()
            await sleep_ms(SEND_STATE_INTERVAL)

    def on_off(self, topic, message):
        action = b"%s" % message

        switch_id = b"a" if match(".*/.*a$", topic) else b"b"

        self.set_switch(switch_id, action)

    def toggle_a_b(self, path, params):
        action = params.get(b"action", None)

        switch_id = b"a" if match(".*/.*a$", path) else b"b"

        self.set_switch(switch_id, action)

    def set_switch(self, switch_id, action):
        settings = Settings().load()

        switch = self.switch_a if switch_id == b"a" else self.switch_b

        if action == b"on":
            switch.on()
            state = b"1"
        else:
            switch.off()
            state = b"0"

        if switch_id == b"a":
            settings.state_a = state
        else:
            settings.state_b = state

        settings.write()
        self.set_state()

    def set_state(self):
        settings = Settings().load()

        state_a = "ON" if settings.state_a == b"1" else "OFF"
        state_b = "ON" if settings.state_b == b"1" else "OFF"

        self.connectivity.set_state({}, state_a, state_b)

try:
    main = Main()
except Exception as e:
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))
    sleep(WAIT_BEFORE_RESET)
    reset()
