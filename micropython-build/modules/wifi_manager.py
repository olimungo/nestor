from network import WLAN, STA_IF, AP_IF, AUTH_OPEN
from uasyncio import get_event_loop, sleep_ms
from blink import Blink
from time import ticks_ms, ticks_diff
from credentials import Credentials

AP_IP = "1.2.3.4"
SERVER_SUBNET = "255.255.255.0"
WAIT_FOR_CONNECT = const(6000)
WAIT_BEFORE_SHUTTING_DOWN_AP = const(25000)
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

        # Make sure that AP is not active
        self.ap_if.active(False)

        self.sta_if.active(False)
        self.sta_if.active(True)

        self.loop = get_event_loop()

        self.loop.create_task(self.check_connected())
        self.connect()

    async def check_connected(self):
        while True:
            while not self.sta_if.isconnected():
                await sleep_ms(CHECK_CONNECTED)

            self.ip = self.sta_if.ifconfig()[0]

            Blink().flash_3_times_fast()

            credentials = Credentials().load()

            print(
                "> Connected to {} with IP: {}".format(
                    credentials.essid.decode("ascii"), self.ip
                )
            )

            self.loop.create_task(self.wait_before_shutting_down_access_point())

            while self.sta_if.isconnected():
                await sleep_ms(CHECK_CONNECTED)

            print("> Disconnected from routeur")

            self.loop.create_task(self.start_access_point())

    def connect(self):
        self.loop.create_task(self.connect_async())

    async def connect_async(self):
        credentials = Credentials().load()

        if credentials.is_valid() and credentials.essid != b"" and credentials.password != b"":
            hidden_pass = "*" * len(credentials.password)

            print(
                "> Connecting to {:s}/{:s}".format(
                    credentials.essid, hidden_pass
                )
            )

            self.sta_if.active(False)
            self.sta_if.active(True)

            self.sta_if.connect(credentials.essid, credentials.password)

            await sleep_ms(WAIT_FOR_CONNECT)

        if not self.sta_if.isconnected():
            self.loop.create_task(self.start_access_point())

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

    async def wait_before_shutting_down_access_point(self):
        # Wait a bit before shutting down in case a web client is waiting to get
        # the IP address from the router
        await sleep_ms(WAIT_BEFORE_SHUTTING_DOWN_AP)

        # Make sure that after having waited, the connection is still active
        if self.sta_if.isconnected():
            self.shutdown_access_point()

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

            self.ssids = list(set(self.ssids))
            self.ssids.sort()

        return b'{"ssids": [%s]}' % (",".join(self.ssids))