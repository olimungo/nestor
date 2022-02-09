from uasyncio import get_event_loop, sleep_ms
from machine import reset, Pin
from time import sleep
from gc import collect, mem_free
from re import match
from math import floor
from connectivity_manager import ConnectivityManager
from settings import Settings

PUBLIC_NAME = b"Switch"
BROKER_NAME = b"nestor.local"
# BROKER_NAME = b"death-star.local"
MQTT_TOPIC_NAME = b"switches"
MQTT_DEVICE_TYPE = b"SWITCH"
HTTP_DEVICE_TYPE = b"SWITCH"
# HTTP_DEVICE_TYPE = b"DOUBLE-SWITCH"

WAIT_BEFORE_RESET = const(10) # seconds

USE_MDNS = True
USE_MQTT = True

PIN_SWITCH_A = const(5)  # D1
PIN_SWITCH_B = const(4)  # D2

WAIT_FOR_TIMER = const(1000)

class Main:
    task_handle_timer = None

    def __init__(self):
        self.settings = Settings().load()

        url_routes = {
            b"/action/toggle-a": self.toggle_a_b,
            b"/action/toggle-b": self.toggle_a_b,
            b"/action/timer-a": self.timer_a_b,
            b"/action/timer-b": self.timer_a_b
        }

        mqtt_subscribe_topics = {
            b"on": self.on_off,
            b"off": self.on_off
        }

        self.connectivity = ConnectivityManager(PUBLIC_NAME, BROKER_NAME, url_routes,
            MQTT_TOPIC_NAME, mqtt_subscribe_topics,
            MQTT_DEVICE_TYPE, HTTP_DEVICE_TYPE,
            self.connectivity_up, self.connectivity_down,
            use_ntp=True, use_mdns=USE_MDNS, use_mqtt=USE_MQTT)

        self.set_state()

        self.switch_a = Pin(PIN_SWITCH_A, Pin.OUT)
        self.switch_b = Pin(PIN_SWITCH_B, Pin.OUT)

        self.switch_a.on() if self.settings.state_a == b"1" else self.switch_a.off()
        self.switch_b.on() if self.settings.state_b == b"1" else self.switch_b.off()

        self.loop = get_event_loop()
        self.loop.run_forever()
        self.loop.close()

    def connectivity_up(self):
        if self.settings.timer_a != b"0" or self.settings.timer_b != b"0":
            self.task_handle_timer = self.loop.create_task(self.handle_timer())

        collect()
        print("> Free mem after all services up: {}".format(mem_free()))

    def connectivity_down(self):
        pass

    async def handle_timer(self):
        all_timers_expired = False

        while not all_timers_expired:
            if self.settings.timer_a != b"0" or self.settings.timer_b != b"0":
                hour1, hour2, minute1, minute2, _, _ = self.connectivity.ntp.get_time()
                now = ((hour1 * 10 + hour2) * 60) + (minute1 * 10 + minute2)

                if self.check_timer(self.settings.timer_a, now):
                    self.settings.timer_a = b"0"
                    self.settings.write()
                    self.set_switch(b"a", b"off")

                if self.check_timer(self.settings.timer_b, now):
                    self.settings.timer_b = b"0"
                    self.settings.write()
                    self.set_switch(b"b", b"off")

                await sleep_ms(WAIT_FOR_TIMER)
            else:
                all_timers_expired = True
                self.task_handle_timer = None

    def check_timer(self, timer, now):
        if timer == b"0":
            return False
        else:
            split = timer.split(b":")
            target = int(split[0]) * 60 + int(split[1])

            return now >= target and now - target < 5

    def on_off(self, topic, message):
        action = b"%s" % message
        switch_id = b"b" if match(".*/.*b$", topic) else b"a"

        self.set_switch(switch_id, action)

    def toggle_a_b(self, path, params):
        action = params.get(b"action", None)

        switch_id = b"a" if match(".*/.*a$", path) else b"b"

        self.set_switch(switch_id, action)

    def timer_a_b(self, path, params):
        delay = params.get(b"minutes", None)

        if delay:
            hour1, hour2, minute1, minute2, _, _ = self.connectivity.ntp.get_time()

            hour = hour1 * 10 + hour2
            minute = minute1 * 10 + minute2

            minutes_delay = hour * 60 + minute + int(delay)
            minutes_target = minutes_delay % (24 * 60)
            new_hour = floor(minutes_target / 60)
            new_minute = minutes_target % 60
            timer = b"%s:%s" % (f'{new_hour:02}', f'{new_minute:02}')

            if match(".*/.*a$", path):
                self.settings.timer_a = timer
                self.set_switch(b"a", b"on")
            else:
                self.settings.timer_b = timer
                self.set_switch(b"b", b"on")

            self.settings.write()
            
            self.set_state()

            if not self.task_handle_timer:
                self.task_handle_timer = self.loop.create_task(self.handle_timer())

            return b'{"timer": "%s"}' % timer

    def set_switch(self, switch_id, action):
        print(f'> Turning switch {switch_id:s}: {action:s}')

        settings = Settings().load()
        switch = self.switch_a if switch_id == b"a" else self.switch_b

        if action == b"on":
            switch.on()
            state = b"1"
        else:
            switch.off()
            state = b"0"

            if switch_id == b"a":
                self.settings.timer_a = b"0"
            else:
                self.settings.timer_b = b"0"

        if switch_id == b"a":
            self.settings.state_a = state
        else:
            self.settings.state_b = state

        self.settings.write()
        self.set_state()

    def set_state(self):
        state_a = "ON" if self.settings.state_a == b"1" else "OFF"
        state_b = "ON" if self.settings.state_b == b"1" else "OFF"

        http_config = {b"timer": b"%s,%s" % (self.settings.timer_a, self.settings.timer_b)}

        http_config = {b"timer": b"%s,%s" % (self.settings.timer_a, self.settings.timer_b)}

        if HTTP_DEVICE_TYPE != b"DOUBLE-SWITCH":
            state_b = None

        self.connectivity.set_state(http_config, state_a, state_b)
try:
    Main()
except Exception as e:
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))
    sleep(WAIT_BEFORE_RESET)
    reset()
