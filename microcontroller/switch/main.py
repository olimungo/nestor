from uasyncio import get_event_loop, sleep_ms
from gc import collect, mem_free
from machine import reset, Pin
from time import sleep
from network import WLAN, STA_IF

from WifiManager import WifiManager
from HttpServer import HttpServer
from mDnsServer import mDnsServer
from MqttManager import MqttManager
from Settings import Settings
from Credentials import Credentials

# from UdpServer import UdpServer

PUBLIC_NAME = b"Switch"
BROKER_NAME = b"nestor.local"
MQTT_TOPIC_NAME = b"switches"

PIN_SWITCH_1 = 5  # D1
PIN_SWITCH_2 = 0  # D3


class Main:
    def __init__(self):
        self.sta_if = WLAN(STA_IF)
        self.settings = Settings().load()
        self.credentials = Credentials().load()
        # self.udps = UdpServer()

        self.switch1 = Pin(PIN_SWITCH_1, Pin.OUT)
        self.switch2 = Pin(PIN_SWITCH_2, Pin.OUT)

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
            b"/action/toggle": self.toggle,
            b"/settings/values": self.settings_values,
            b"/settings/net": self.settings_net,
            b"/settings/ssids": self.get_ssids,
        }

        self.http = HttpServer(routes)
        print("> HTTP server up and running")

        self.loop = get_event_loop()
        self.loop.create_task(self.check_wifi())
        self.loop.create_task(self.check_mqtt())
        self.loop.create_task(self.send_state())
        self.loop.run_forever()
        self.loop.close()

    async def check_wifi(self):
        while True:
            await sleep_ms(2000)

            while not self.sta_if.isconnected():
                await sleep_ms(1000)

            self.send_state_mqtt()

            while self.sta_if.isconnected():
                await sleep_ms(1000)

    async def check_mqtt(self):
        while True:
            while self.mqtt.connected:
                self.check_message_mqtt()
                await sleep_ms(100)

            while not self.mqtt.connected:
                await sleep_ms(1000)

            self.send_state_mqtt()

    def check_message_mqtt(self):
        try:
            message = self.mqtt.check_messages()

            if message:
                if message == b"up":
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
            b'{"ip": "%s", "netId": "%s", "group": "%s", "state1": "%s", "state2": "%s", "essid": "%s"}'
            % (
                self.wifi.ip,
                self.settings.net_id,
                self.settings.group,
                self.settings.state1,
                self.settings.state2,
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

    def toggle(self, params):
        id = params.get(b"id", None)
        action = params.get(b"action", None)

        if id and action:
            if id == b"1":
                switch = self.switch1
            else:
                switch = self.switch2

            if action == b"on":
                switch.on()
                value = b"1"
            else:
                switch.off()
                value = b"0"

            if id == 1:
                self.settings.switch1 = value
            else:
                self.settings.switch2 = value

            self.settings.write()

    def settings_net(self, params):
        id = params.get(b"id", None)

        if id:
            self.settings.net_id = id
            self.settings.write()
            self.mdns.set_net_id(id)

            self.wifi.set_ap_essid(b"%s-%s" % (PUBLIC_NAME, id))
            self.mdns.set_net_id(id)
            self.mqtt.set_net_id(id)

    async def send_state(self):
        while True:
            self.send_state_mqtt()
            await sleep_ms(30000)

    def send_state_mqtt(self):
        try:
            state = b'{"group": "%s", "state1": "%s", "state2": "%s"}' % (
                self.settings.group,
                self.settings.state1,
                self.settings.state2,
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
