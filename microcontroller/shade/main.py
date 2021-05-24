from uasyncio import get_event_loop, sleep_ms
from gc import collect, mem_free
from machine import reset
from time import sleep
from network import WLAN, STA_IF
from re import match

from WifiManager import WifiManager
from HttpServer import HttpServer
from mDnsServer import mDnsServer
from MqttManager import MqttManager
from Motor import Motor
from Settings import Settings
from Credentials import Credentials
from Tags import Tags

PUBLIC_NAME = b"Shade"
# BROKER_NAME = b"nestor.local"
BROKER_NAME = b"192.168.0.215"
MQTT_TOPIC_NAME = b"shades"
DEVICE_TYPE = b"MOTOR-V"

STARTUP_DELAY = const(1000 * 2)
WIFI_CHECK_CONNECTED_INTERVAL = const(1000)
MQTT_STATUS_INTERVAL = const(1000 * 5)
MQTT_CHECK_MESSAGE_INTERVAL = const(250)
MQTT_CHECK_CONNECTED_INTERVAL = const(1000)


class Main:
    def __init__(self):
        self.sta_if = WLAN(STA_IF)
        self.settings = Settings().load()
        self.credentials = Credentials().load()
        self.tags = Tags().load()

        self.wifi = WifiManager(b"%s-%s" % (PUBLIC_NAME, self.settings.net_id))
        self.mdns = mDnsServer(PUBLIC_NAME.lower(), self.settings.net_id)
        self.mqtt = MqttManager(
            self.mdns, BROKER_NAME, self.settings.net_id, MQTT_TOPIC_NAME
        )

        routes = {
            b"/": b"./index.html",
            b"/index.html": b"./index.html",
            b"/scripts.js": b"./scripts.js",
            b"/style.css": b"./style.css",
            b"/favicon.ico": self.favicon,
            b"/connect": self.connect,
            b"/action/go-up": self.go_up,
            b"/action/go-down": self.go_down,
            b"/action/stop": self.stop,
            b"/settings/values": self.settings_values,
            b"/settings/net-id": self.settings_net_id,
            b"/settings/reverse-motor": self.reverse_motor,
            b"/settings/ssids": self.get_ssids,
        }

        self.http = HttpServer(routes)
        print("> HTTP server up and running")

        self.motor = Motor()

        self.loop = get_event_loop()
        self.loop.create_task(self.check_wifi())
        self.loop.create_task(self.check_mqtt())
        self.loop.create_task(self.send_state())
        self.loop.run_forever()
        self.loop.close()

    async def check_wifi(self):
        while True:
            await sleep_ms(STARTUP_DELAY)

            while not self.sta_if.isconnected():
                await sleep_ms(WIFI_CHECK_CONNECTED_INTERVAL)

            self.send_state_mqtt()

            while self.sta_if.isconnected():
                await sleep_ms(WIFI_CHECK_CONNECTED_INTERVAL)

    async def check_mqtt(self):
        while True:
            while self.mqtt.connected:
                self.check_message_mqtt()

                if self.motor.check_stopped_by_ir_sensor():
                    self.send_state_mqtt()

                await sleep_ms(MQTT_CHECK_MESSAGE_INTERVAL)

            while not self.mqtt.connected:
                await sleep_ms(MQTT_CHECK_CONNECTED_INTERVAL)

            self.send_state_mqtt()

    def check_message_mqtt(self):
        try:
            message = self.mqtt.check_messages()

            if message:
                if match("add-tag/", message):
                    tag = message.split(b"/")[1]
                    self.tags.append(tag)
                elif match("remove-tag/", message):
                    tag = message.split(b"/")[1]
                    self.tags.remove(tag)
                elif message == b"up":
                    self.go_up()
                elif message == b"down":
                    self.go_down()
                elif message == b"stop":
                    self.stop()

        except Exception as e:
            print("> Main.check_message_mqtt exception: {}".format(e))

    def settings_values(self, params):
        essid = self.credentials.essid

        if not essid:
            essid = b""

        result = (
            b'{"ip": "%s", "netId": "%s", "motorReversed": "%s", "essid": "%s"}'
            % (
                self.wifi.ip,
                self.settings.net_id,
                self.settings.motor_reversed,
                essid,
            )
        )

        return result

    def favicon(self, params):
        print("> NOT sending the favico :-)")

    def connect(self, params):
        self.credentials.essid = params.get(b"essid", None)
        self.credentials.password = params.get(b"password", None)
        self.credentials.write()

        self.loop.create_task(self.wifi.connect())

    def go_up(self, params=None):
        self.motor.go_up()
        self.send_state_mqtt()

    def go_down(self, params=None):
        self.motor.go_down()
        self.send_state_mqtt()

    def stop(self, params=None):
        self.motor.stop()
        self.send_state_mqtt()

    def settings_net_id(self, params):
        id = params.get(b"id", None)

        if id:
            self.settings.net_id = id
            self.settings.write()
            self.mdns.set_net_id(id)

            self.wifi.set_ap_essid(b"%s-%s" % (PUBLIC_NAME, id))
            self.mdns.set_net_id(id)
            self.mqtt.set_net_id(id)

    def reverse_motor(self, params):
        motor_reversed = self.settings.motor_reversed

        if motor_reversed == b"0":
            motor_reversed = b"1"
        else:
            motor_reversed = b"0"

        self.settings.motor_reversed = motor_reversed
        self.settings.write()

        self.motor.reverse_direction()

    async def send_state(self):
        while True:
            self.send_state_mqtt()

            await sleep_ms(MQTT_STATUS_INTERVAL)

    def send_state_mqtt(self):
        try:
            tags = []

            for tag in self.tags.tags:
                tags.append("\"%s\"" % (tag.decode('utf-8')))
                
            state = b'{"ip": "%s", "type": "%s", "state": "%s", "tags": [%s] }' % (
                self.wifi.ip,
                DEVICE_TYPE,
                self.motor.get_state(),
                ",".join(tags)
            )
            self.mqtt.publish_state(state)
        except Exception as e:
            print("> Main.send_state_mqtt exception: {}".format(e))

    def get_ssids(self, params):
        return self.wifi.get_ssids()


try:
    collect()
    print("Free mem: {}".format(mem_free()))

    main = Main()
except Exception as e:
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))
    sleep(10)
    reset()
