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
from Clock import Clock
from Settings import Settings
from Credentials import Credentials
from Tags import Tags

PUBLIC_NAME = b"Clock"
BROKER_NAME = b"nestor.local"
# BROKER_NAME = b"192.168.0.215"
MQTT_TOPIC_NAME = b"clocks"
DEVICE_TYPE = b"CLOCK"

ORANGE = (255, 98, 0)
SPINNER_RATE = const(120)

STARTUP_DELAY = const(1000 * 2)
WIFI_CHECK_CONNECTED_INTERVAL = const(1000)
MQTT_STATUS_INTERVAL = const(1000 * 5)
MQTT_CHECK_MESSAGE_INTERVAL = const(250)
MQTT_CHECK_CONNECTED_INTERVAL = const(1000)

class Player:
    GREEN = 0
    RED = 1


class State:
    CLOCK = 0
    SCOREBOARD = 1
    OFF = 2

    STATE_TEXT = ["CLOCK", "SCOREBOARD", "OFF"]


class Main:
    def __init__(self):
        self.sta_if = WLAN(STA_IF)
        self.settings = Settings(state=b"%s" % State.CLOCK).load()
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
            b"/action/color": self.set_color,
            b"/action/clock/display": self.display_clock,
            b"/action/brightness": self.set_brightness,
            b"/action/scoreboard/display": self.display_scoreboard,
            b"/action/scoreboard/green/more": self.scoreboard_green_more,
            b"/action/scoreboard/green/less": self.scoreboard_green_less,
            b"/action/scoreboard/red/more": self.scoreboard_red_more,
            b"/action/scoreboard/red/less": self.scoreboard_red_less,
            b"/action/scoreboard/reset": self.scoreboard_reset,
            b"/settings/values": self.settings_values,
            b"/settings/net-id": self.settings_net_id,
            b"/settings/ssids": self.get_ssids,
        }

        # self.http = HttpServer(routes)
        # print("> HTTP server up and running")

        # self.clock = Clock(self.settings.color)

        # self.loop = get_event_loop()
        # self.loop.create_task(self.check_wifi())
        # self.loop.create_task(self.check_mqtt())
        # self.loop.create_task(self.send_state())
        # self.loop.run_forever()
        # self.loop.close()

    async def check_wifi(self):
        while True:
            self.clock.stop()
            self.clock.play_spinner(SPINNER_RATE, ORANGE)

            await sleep_ms(2000)

            while not self.sta_if.isconnected():
                await sleep_ms(1000)

            self.clock.stop_effect_init = True

            if self.settings.state != b"%s" % State.OFF:
                self.settings.state = b"%s" % State.CLOCK
                self.settings.write()
                self.clock.display()
            else:
                self.clock.clear_all()

            while self.sta_if.isconnected():
                await sleep_ms(1000)

    async def check_mqtt(self):
        while True:
            while self.mqtt.connected:
                self.check_message_mqtt()

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

        except Exception as e:
            print("> Main.check_message_mqtt exception: {}".format(e))

    def settings_values(self, params):
        essid = self.credentials.essid

        if not essid:
            essid = b""

        if self.settings.state == b"%s" % State.OFF:
                l = 0
        else:
            _, _, l = self.clock.hsl

        result = (
            b'{"ip": "%s", "netId": "%s",  "essid": "%s", "brightness": "%s"}'
            % (self.wifi.ip, self.settings.net_id, essid, int(l))
        )

        return result

    def favicon(self, params):
        print("> NOT sending the favico :-)")

    def connect(self, params):
        self.credentials.essid = params.get(b"essid", None)
        self.credentials.password = params.get(b"password", None)
        self.credentials.write()

        self.wifi.connect()

    def display_clock(self, params=None):
        if self.settings.state != b"%s" % State.CLOCK:
            self.settings.state = b"%s" % State.CLOCK
            self.settings.write()
            self.clock.display()

    def display_scoreboard(self, params=None):
        if self.settings.state != b"%s" % State.SCOREBOARD:
            self.clock.stop()
            self.settings.state = b"%s" % State.SCOREBOARD
            self.settings.write()
            self.clock.display_scoreboard()

    def set_color(self, params):
        self.display_clock()

        color = params.get(b"hex", None)

        if color:
            self.clock.set_color(color)

            self.settings.color = color
            self.settings.write()

        _, _, l = self.clock.hsl

        return b'{"brightness": "%s"}' % int(l)

    def scoreboard_green_more(self, params):
        self.scoreboard_update(Player.GREEN, 1)

    def scoreboard_green_less(self, params):
        self.scoreboard_update(Player.GREEN, -1)

    def scoreboard_red_more(self, params):
        self.scoreboard_update(Player.RED, 1)

    def scoreboard_red_less(self, params):
        self.scoreboard_update(Player.RED, -1)

    def scoreboard_update(self, player, increment):
        if player == Player.GREEN:
            self.clock.update_scoreboard_green(increment)
        else:
            self.clock.update_scoreboard_red(increment)

        self.display_scoreboard()

    def set_brightness(self, params):
        l = int(params.get(b"l", 0))

        if l > 0:
            self.display_clock()
            self.clock.set_brightness(l)

            self.settings.color = b"%s" % self.clock.hex
        else:
            self.clock.off()
            self.settings.state = b"%s" % State.OFF

        self.settings.write()

    def scoreboard_reset(self, params):
        self.display_scoreboard()
        self.clock.reset_scoreboard()

    def settings_net_id(self, params):
        id = params.get(b"id", None)

        if id:
            self.settings.net_id = id
            self.settings.write()
            self.mdns.set_net_id(id)

    async def send_state(self):
        while True:
            self.send_state_mqtt()

            await sleep_ms(MQTT_STATUS_INTERVAL)
            
    def send_state_mqtt(self):
        try:
            tags = []

            # for tag in self.tags.tags:
            #     tags.append("\"%s\"" % (tag.decode('utf-8')))

            # state = b'{"ip": "%s", "type": "%s", "state": "%s", "tags": [%s] }' % (
            #     self.wifi.ip,
            #     DEVICE_TYPE,
            #     State.STATE_TEXT[self.settings.state],
            #     ",".join(tags)
            # )

            # self.mqtt.publish_state(state)
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
