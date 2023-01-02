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
DEVICE_TYPE = b"SWITCH"

WAIT_BEFORE_RESET = const(10) # seconds

USE_MDNS = True
USE_MQTT = True
USE_NTP = True

PIN_SWITCH = const(5)  # D1 - GPIO5

WAIT_FOR_TIMER = const(1000)

class Main:
    task_handle_timer = None

    def __init__(self):
        settings = Settings().load()

        url_routes = {
            b"/action/toggle": self.toggle,
            b"/action/timer": self.timer
        }

        mqtt_subscribe_topics = {
            b"on": self.command_on_off,
            b"off": self.command_on_off,
            b"timer": self.command_timer
        }

        self.connectivity = ConnectivityManager(PUBLIC_NAME, BROKER_NAME, url_routes,
            MQTT_TOPIC_NAME, mqtt_subscribe_topics, DEVICE_TYPE,
            self.connectivity_up, self.connectivity_down,
            use_ntp=USE_NTP, use_mdns=USE_MDNS, use_mqtt=USE_MQTT)

        self.set_state()

        self.switch = Pin(PIN_SWITCH, Pin.OUT)

        self.switch.on() if settings.state == b"1" else self.switch.off()

        self.loop = get_event_loop()
        self.loop.run_forever()
        self.loop.close()

    def connectivity_up(self):
        settings = Settings().load()

        if settings.timer != b"0":
            self.task_handle_timer = self.loop.create_task(self.handle_timer())

        collect()
        print("> Free mem after all services up: {}".format(mem_free()))

    def connectivity_down(self):
        pass

    async def handle_timer(self):
        all_timers_expired = False
        settings = Settings().load()

        while not all_timers_expired:
            if settings.timer != b"0":
                hour1, hour2, minute1, minute2, _, _ = self.connectivity.ntp.get_time()
                now = ((hour1 * 10 + hour2) * 60) + (minute1 * 10 + minute2)

                if self.check_timer(settings.timer, now):
                    settings.timer = b"0"
                    settings.write()
                    self.set_switch(b"off")

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

    def command_on_off(self, topic, message):
        action = b"%s" % message
        self.set_switch(action)

    def command_timer(self, topic, message):
        duration = message.split(b"/")

        if len(duration) == 2:
            self.set_timer(duration[1])

    def toggle(self, path, params):
        action = params.get(b"action", None)
        self.set_switch(action)

    def timer(self, path, params):
        duration = params.get(b"minutes", None)
        return self.set_timer(duration)

    def set_timer(self, duration):
        settings = Settings().load()

        hour1, hour2, minute1, minute2, _, _ = self.connectivity.ntp.get_time()

        hour = hour1 * 10 + hour2
        minute = minute1 * 10 + minute2

        minutes_duration = hour * 60 + minute + int(duration)
        minutes_target = minutes_duration % (24 * 60)
        new_hour = floor(minutes_target / 60)
        new_minute = minutes_target % 60
        timer = b"%s:%s" % (f'{new_hour:02}', f'{new_minute:02}')

        settings.timer = timer

        print(f"> Timer set for {timer:s}")

        self.set_switch(b"on")

        settings.write()
        
        self.set_state()

        if not self.task_handle_timer:
            self.task_handle_timer = self.loop.create_task(self.handle_timer())

        return b'{"timer": "%s"}' % timer

    def set_switch(self, action):
        print(f"> Turning switch {action:s}")

        settings = Settings().load()

        if action == b"on":
            self.switch.on()
            state = b"1"
        else:
            self.switch.off()
            state = b"0"
            settings.timer = b"0"

        settings.state = state

        settings.write()

        self.set_state()

    def set_state(self):
        settings = Settings().load()

        state = b"ON" if settings.state == b"1" else b"OFF"
        http_config = {b"timer": b"%s" % (settings.timer)}

        self.connectivity.set_state(http_config, state)
try:
    Main()
except Exception as e:
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))
    sleep(WAIT_BEFORE_RESET)
    reset()
