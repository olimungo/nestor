from network import WLAN, STA_IF, AP_IF, AUTH_OPEN
from uasyncio import get_event_loop, sleep_ms
from Blink import Blink
from time import ticks_ms, ticks_diff

from Credentials import Credentials

AP_IP = "1.2.3.4"
WAIT_FOR_CONNECT = const(6000)
WAIT_BEFORE_RECONNECT = const(60000)
WAIT_BEFORE_AP_SHUTDOWN = const(30000)
SCAN_SSIDS_REFRESH = const(30000)
CHECK_CONNECTED = const(250)

class WifiManager:
    ip = "0.0.0.0"
    ssids = []
    ssids_timestamp = 0

    def __init__(self, ap_essid):
        self.sta_if = WLAN(STA_IF)
        self.ap_if = WLAN(AP_IF)
        self.ap_essid = ap_essid
        self.credentials = Credentials()

        # Make sure that AP is not active
        self.ap_if.active(False)

        self.sta_if.active(False)
        self.sta_if.active(True)

        self.loop = get_event_loop()
        self.loop.create_task(self.check_connected())
        self.loop.create_task(self.check_connection())

    async def check_connected(self):
        while True:
            while not self.sta_if.isconnected():
                await sleep_ms(CHECK_CONNECTED)

            self.ip = self.sta_if.ifconfig()[0]

            Blink().flash3TimesFast()

            print(
                "> Connected to {} with IP: {}".format(
                    self.credentials.essid.decode("ascii"), self.ip
                )
            )

            while self.sta_if.isconnected():
                await sleep_ms(CHECK_CONNECTED)

    async def check_connection(self):
        while True:
            if not self.sta_if.isconnected():
                self.connect()

            await sleep_ms(WAIT_BEFORE_RECONNECT)

    def connect(self):
        self.loop.create_task(self.connect_async())

    async def connect_async(self):
        if self.credentials.load().is_valid():
            print(
                "> Connecting to {:s}/{:s}".format(
                    self.credentials.essid, self.credentials.password
                )
            )

            self.sta_if.active(False)
            self.sta_if.active(True)

            self.sta_if.connect(self.credentials.essid, self.credentials.password)

            await sleep_ms(WAIT_FOR_CONNECT)

        if self.sta_if.isconnected():
            # Leave a bit of time so the client can retrieve the Wifi IP address
            await sleep_ms(WAIT_BEFORE_AP_SHUTDOWN)
            self.shutdown_access_point()
        else:
            self.loop.create_task(self.start_access_point())

    async def start_access_point(self):
        if not self.ap_if.active():
            self.ap_if.active(True)

            while not self.ap_if.active():
                await sleep_ms(CHECK_CONNECTED)

            self.ip = AP_IP

            # IP address, netmask, gateway, DNS
            self.ap_if.ifconfig((self.ip, "255.255.255.0", self.ip, self.ip))

            self.ap_if.config(essid=self.ap_essid, authmode=AUTH_OPEN)
            print(
                "> AP mode configured: {} ".format(self.ap_essid.decode("utf-8")),
                self.ap_if.ifconfig(),
            )

    def shutdown_access_point(self):
        if self.ap_if.active():
            print("> Shuting down AP")
            self.ap_if.active(False)

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

            self.ssids.sort()

        return b'{"ssids": [%s]}' % (",".join(self.ssids))