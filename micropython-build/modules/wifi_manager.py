from machine import reset
from network import WLAN, STA_IF, AP_IF, AUTH_OPEN
from uasyncio import get_event_loop, sleep_ms
from blink import Blink
from time import ticks_ms, ticks_diff
from credentials import Credentials

NO_IP = "0.0.0.0"
AP_IP = "1.2.3.4"
SERVER_SUBNET = "255.255.255.0"
MAX_WAIT_FOR_CONNECTION_CHECK = const(15)
WAIT_FOR_CONNECTION_CHECK = const(1000)
WAIT_BETWEEN_CONNECT = const(10000)
WAIT_BEFORE_RESET = const(7000)
LAST_ACTIVITY_TIMEOUT = const(30000)
SCAN_SSIDS_REFRESH = const(30000)
CHECK_CONNECTED = const(250)

class WifiManager:
    ip = NO_IP
    ssids = []
    ssids_timestamp = 0
    last_http_activity = -LAST_ACTIVITY_TIMEOUT

    def __init__(self, ap_essid):
        self.sta_if = WLAN(STA_IF)
        self.ap_if = WLAN(AP_IF)
        self.ap_essid = ap_essid

        # Make sure that AP is not active
        self.ap_if.active(False)

        # Reset the station
        self.sta_if.active(False)
        self.sta_if.active(True)

        self.loop = get_event_loop()

        self.loop.create_task(self.check_mode())

    async def check_mode(self):
        await self.connect_to_station()

        if self.sta_if.isconnected():
            self.loop.create_task(self.station_mode())
        else:
            self.loop.create_task(self.access_point_mode())

    async def station_mode(self):
        print("> Station mode")

        while self.sta_if.isconnected():
            await sleep_ms(CHECK_CONNECTED)

        self.sta_if.disconnect()
        self.ip = NO_IP

        self.loop.create_task(self.access_point_mode())

    async def access_point_mode(self):
        print("> AP mode")

        await self.start_access_point()

        while not self.sta_if.isconnected():
            if ticks_diff(ticks_ms(), self.last_http_activity + LAST_ACTIVITY_TIMEOUT) > 0:
                await self.connect_to_station()

            if not self.sta_if.isconnected():
                await sleep_ms(WAIT_BETWEEN_CONNECT)

        self.loop.create_task(self.station_mode())

    def connect(self):
        self.loop.create_task(self.connect_async())

    async def connect_async(self):
        await self.connect_to_station()

    async def connect_to_station(self):
        credentials = Credentials().load()

        if credentials.is_valid() and credentials.essid != b"" and credentials.password != b"":
            hidden_pass = "*" * len(credentials.password)

            print(
                "> Connecting to {:s}/{:s}".format(
                    credentials.essid, hidden_pass
                )
            )

            self.sta_if.connect(credentials.essid, credentials.password)

            retry = 0

            while retry < MAX_WAIT_FOR_CONNECTION_CHECK and not self.sta_if.isconnected():
                retry = retry + 1
                await sleep_ms(WAIT_FOR_CONNECTION_CHECK)

            if not self.sta_if.isconnected():
                print("> Connection not successful!")
                self.sta_if.disconnect()
            else:
                self.ip = self.sta_if.ifconfig()[0]

                Blink().flash_3_times_fast()

                credentials = Credentials().load()

                print(
                    "> Connected to {} with IP: {}".format(
                        credentials.essid.decode("ascii"), self.ip
                    )
                )

                if self.ap_if.active():
                    await sleep_ms(WAIT_BEFORE_RESET)
                    reset()

    async def start_access_point(self):
        if not self.ap_if.active():
            self.ap_if.active(True)

            while not self.ap_if.active():
                await sleep_ms(CHECK_CONNECTED)

            self.ip = AP_IP

            # IP address, netmask, gateway, DNS
            self.ap_if.ifconfig((AP_IP, SERVER_SUBNET, AP_IP, AP_IP))

            self.ap_if.config(essid=self.ap_essid, authmode=AUTH_OPEN)
            print(
                "> AP mode configured: {} ".format(self.ap_essid.decode("utf-8")),
                self.ap_if.ifconfig(),
            )

    def set_ap_essid(self, ap_essid):
        self.ap_essid = ap_essid

    def get_ssids(self):
        now = ticks_ms()

        if len(self.ssids) == 0 or ticks_diff(now, self.ssids_timestamp + SCAN_SSIDS_REFRESH) > 0:
            ssids = self.sta_if.scan()
            self.ssids_timestamp = now
            self.ssids = []

            for ssid in ssids:
                self.ssids.append('"%s"' % ssid[0].decode("ascii"))

            self.ssids = list(set(self.ssids))
            self.ssids.sort()

        return b'{"ssids": [%s]}' % (",".join(self.ssids))

    def set_http_activity(self):
        self.last_http_activity = ticks_ms()