from uasyncio import get_event_loop, sleep_ms
from gc import collect, mem_free
from machine import reset
from time import sleep
from network import WLAN, STA_IF

from WifiManager import WifiManager
from HttpServer import HttpServer
from mDnsServer import mDnsServer
from Clock import Clock
from Settings import Settings
from Credentials import Credentials

PUBLIC_NAME = b"Clock"
ORANGE = (255, 98, 0)
SPINNER_RATE = const(120)


class Player:
    GREEN = 0
    RED = 1


class Mode:
    CLOCK = 0
    SCOREBOARD = 1


class Main:
    def __init__(self):
        self.sta_if = WLAN(STA_IF)
        self.settings = Settings().load()
        self.credentials = Credentials().load()
        self.mode = Mode.CLOCK

        self.wifi = WifiManager(b"%s-%s" % (PUBLIC_NAME, self.settings.net_id))
        self.mdns = mDnsServer(PUBLIC_NAME.lower(), self.settings.net_id)

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
            b"/settings/net": self.settings_net,
            b"/settings/group": self.settings_group,
        }

        self.http = HttpServer(routes)
        print("> HTTP server up and running")

        self.clock = Clock(self.settings.color)

        self.loop = get_event_loop()
        self.loop.create_task(self.check_wifi())
        self.loop.run_forever()
        self.loop.close()

    async def check_wifi(self):
        while True:
            self.clock.stop()
            self.clock.play_spinner(SPINNER_RATE, ORANGE)

            await sleep_ms(2000)

            while not self.sta_if.isconnected():
                await sleep_ms(1000)

            self.clock.stop_effect_init = True
            self.clock.display()

            while self.sta_if.isconnected():
                await sleep_ms(1000)

    def settings_values(self, params):
        essid = self.credentials.essid

        if not essid:
            essid = b""

        _, _, l = self.clock.hsl

        result = (
            b'{"ip": "%s", "netId": "%s", "group": "%s", "essid": "%s", "brightness": "%s"}'
            % (self.wifi.ip, self.settings.net_id, self.settings.group, essid, int(l))
        )

        return result

    def favicon(self, params):
        print("> NOT sending the favico :-)")

    def connect(self, params):
        self.credentials.essid = params.get(b"essid", None)
        self.credentials.password = params.get(b"password", None)
        self.credentials.write()

        self.loop.create_task(self.wifi.connect())

    def display_clock(self, params=None):
        if self.mode == Mode.SCOREBOARD:
            self.mode = Mode.CLOCK
            self.clock.display()

    def display_scoreboard(self, params=None):
        if self.mode == Mode.CLOCK:
            self.clock.stop()
            self.mode = Mode.SCOREBOARD
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

        self.display_clock()
        self.clock.set_brightness(l)

        self.settings.color = b"%s" % self.clock.hex
        self.settings.write()

    def scoreboard_reset(self, params):
        self.display_scoreboard()
        self.clock.reset_scoreboard()

    def settings_net(self, params):
        id = params.get(b"id", None)

        if id:
            self.settings.net_id = id
            self.settings.write()
            self.mdns.set_net_id(id)

    def settings_group(self, params):
        name = params.get(b"name", None)

        if name:
            self.settings.group = name
            self.settings.write()


try:
    collect()
    print("Free mem: {}".format(mem_free()))

    main = Main()
except Exception as e:
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))
    sleep(10)
    reset()