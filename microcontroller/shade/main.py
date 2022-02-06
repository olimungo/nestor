from uasyncio import get_event_loop
from machine import reset
from time import sleep
from gc import collect, mem_free
from connectivity_manager import ConnectivityManager
from settings import Settings
from motor import Motor

PUBLIC_NAME = b"Shade"
BROKER_NAME = b"nestor.local"
# BROKER_NAME = b"death-star.local"
MQTT_TOPIC_NAME = b"shades"
MQTT_DEVICE_TYPE = b"SHADE"
HTTP_DEVICE_TYPE = b"SHADE"

WAIT_BEFORE_RESET = const(10) # seconds

USE_MDNS = True
USE_MQTT = True

class Main:
    def __init__(self):
        url_routes = {
            b"/action/go-up": self.go_up,
            b"/action/go-down": self.go_down,
            b"/action/stop": self.stop,
            b"/settings/reverse-motor": self.reverse_motor,
        }

        mqtt_subscribe_topics = {
            b"up": self.mqtt_go_up,
            b"down": self.mqtt_go_down,
            b"stop": self.mqtt_stop
        }

        self.connectivity = ConnectivityManager(PUBLIC_NAME, BROKER_NAME, url_routes,
            MQTT_TOPIC_NAME, mqtt_subscribe_topics,
            MQTT_DEVICE_TYPE, HTTP_DEVICE_TYPE,
            self.connectivity_up, self.connectivity_down,
            use_ntp=True, use_mdns=USE_MDNS, use_mqtt=USE_MQTT)

        self.motor = Motor()
        
        self.set_state()

        self.loop = get_event_loop()
        self.loop.run_forever()
        self.loop.close()

    def connectivity_up(self):
        collect()
        print("> Free mem after all services up: {}".format(mem_free()))

    def connectivity_down(self):
        pass

    def mqtt_go_up(self, topic, message):
        self.go_up()

    def mqtt_go_down(self, topic, message):
        self.go_down()

    def mqtt_stop(self, topic, message):
        self.stop()

    def go_up(self, path=None, params=None):
        self.motor.go_up()
        self.set_state()

    def go_down(self, path=None, params=None):
        self.motor.go_down()
        self.set_state()

    def stop(self, path=None, params=None):
        self.motor.stop()
        self.set_state()

    def reverse_motor(self, path, params):
        settings = Settings().load()
        motor_reversed = settings.motor_reversed

        if motor_reversed == b"0":
            motor_reversed = b"1"
        else:
            motor_reversed = b"0"

        settings.motor_reversed = motor_reversed
        settings.write()

        self.motor.reverse_direction()
        self.set_state()

    def set_state(self):
        settings = Settings().load()
        
        http_config = {b"motorReversed": settings.motor_reversed}

        self.connectivity.set_state(http_config, self.motor.get_state())

try:
    main = Main()
except Exception as e:
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))
    sleep(WAIT_BEFORE_RESET)
    reset()
