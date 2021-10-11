from uasyncio import get_event_loop, sleep_ms
from machine import reset
from time import sleep
from gc import collect, mem_free
from network import WLAN, STA_IF, AP_IF
from re import match
from wifi_manager import WifiManager
from http_server import HttpServer
from mdns_server import mDnsServer
from mqtt_manager import MqttManager
from settings import Settings
from tags import Tags
from motor import Motor

DEVICE_TYPE = b"SHADE"
PUBLIC_NAME = b"Shade"
BROKER_NAME = b"nestor.local"
# BROKER_NAME = b"deathstar.local"
MQTT_TOPIC_NAME = b"shades"

CHECK_CONNECTED = const(250) # milliseconds
WAIT_BEFORE_RESET = const(10) # seconds
MQTT_CHECK_MESSAGE_INTERVAL = const(250) # milliseconds
MQTT_CHECK_CONNECTED_INTERVAL = const(1000) # milliseconds

class Main:
    def __init__(self):
        self.sta_if = WLAN(STA_IF)
        self.ap_if = WLAN(AP_IF)
        settings = Settings().load()

        self.wifi = WifiManager(b"%s-%s" % (PUBLIC_NAME, settings.net_id))
        self.mdns = mDnsServer(PUBLIC_NAME.lower(), settings.net_id)
        self.mqtt = MqttManager(
            self.mdns, BROKER_NAME, MQTT_TOPIC_NAME, DEVICE_TYPE
        )

        routes = {
            b"/action/go-up": self.go_up,
            b"/action/go-down": self.go_down,
            b"/action/stop": self.stop,
            b"/settings/values": self.settings_values,
            b"/settings/reverse-motor": self.reverse_motor,
        }

        self.http = HttpServer(routes, self.wifi, self.mdns)

        self.motor = Motor()

        self.loop = get_event_loop()
        self.loop.create_task(self.check_connected())
        self.loop.create_task(self.check_mqtt())
        self.loop.run_forever()
        self.loop.close()

    async def check_connected(self):
        while True:
            while not self.sta_if.isconnected() or self.ap_if.active():
                await sleep_ms(CHECK_CONNECTED)

            self.set_state()

            while self.sta_if.isconnected():
                await sleep_ms(CHECK_CONNECTED)

    async def check_mqtt(self):
        while True:
            while self.mqtt.connected:
                self.check_message_mqtt()

                if self.motor.check_stopped_by_ir_sensor():
                    self.set_state()

                await sleep_ms(MQTT_CHECK_MESSAGE_INTERVAL)

            while not self.mqtt.connected:
                await sleep_ms(MQTT_CHECK_CONNECTED_INTERVAL)

            self.set_state()

    def check_message_mqtt(self):
        try:
            message = self.mqtt.check_messages()
            tags = Tags().load()

            if message:
                if match("add-tag/", message):
                    tag = message.split(b"/")[1]
                    tags.append(tag)
                    self.set_state()
                elif match("remove-tag/", message):
                    tag = message.split(b"/")[1]
                    tags.remove(tag)
                    self.set_state()
                elif message == b"up":
                    self.go_up()
                elif message == b"down":
                    self.go_down()
                elif message == b"stop":
                    self.stop()


        except Exception as e:
            print("> Main.check_message_mqtt exception: {}".format(e))

    def settings_values(self, params):
        settings = Settings().load()

        result = (
            b'{"ip": "%s", "netId": "%s", "motorReversed": "%s"}'
            % (
                self.wifi.ip,
                settings.net_id,
                settings.motor_reversed,
            )
        )

        return result

    def go_up(self, params=None):
        self.motor.go_up()
        self.set_state()

    def go_down(self, params=None):
        self.motor.go_down()
        self.set_state()

    def stop(self, params=None):
        self.motor.stop()
        self.set_state()

    def reverse_motor(self, params):
        settings = Settings().load()
        motor_reversed = settings.motor_reversed

        if motor_reversed == b"0":
            motor_reversed = b"1"
        else:
            motor_reversed = b"0"

        settings.motor_reversed = motor_reversed
        settings.write()

        self.motor.reverse_direction()

    def set_state(self):
        self.mqtt.set_state(self.motor.get_state())

try:
    collect()
    print("Free mem: {}".format(mem_free()))

    main = Main()
except Exception as e:
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))
    sleep(WAIT_BEFORE_RESET)
    reset()
