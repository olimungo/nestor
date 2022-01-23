from machine import reset
from network import WLAN, STA_IF, AP_IF, AUTH_OPEN
from uasyncio import get_event_loop, sleep_ms
from blink import Blink
from time import ticks_ms, ticks_diff
from credentials import Credentials

NO_IP = b"0.0.0.0"
AP_IP = b"1.2.3.4"
SERVER_SUBNET = "255.255.255.0"
MAX_WAIT_FOR_CONNECTION_CHECK = const(10)
WAIT_FOR_CONNECTION_CHECK = const(1000)
WAIT_BETWEEN_CONNECT = const(60000)
WAIT_BEFORE_RESET = const(15000)
SCAN_SSIDS_REFRESH = const(30000)
CHECK_CONNECTED = const(250)
WAIT_FOR_BLINK = const(1000)

class WifiManager:
    ip = NO_IP
    ssids = []
    ssids_timestamp = 0

    def __init__(self, access_point_essid, callback_connection_success, callback_connection_fail, callback_access_point_active, callback_set_station_ip):
        self.station = WLAN(STA_IF)
        self.acess_point = WLAN(AP_IF)
        self.access_point_essid = access_point_essid
        self.callback_connection_success = callback_connection_success
        self.callback_connection_fail = callback_connection_fail
        self.callback_access_point_active = callback_access_point_active
        self.callback_set_station_ip = callback_set_station_ip

        # Make sure that AP is not active
        self.acess_point.active(False)

        # Reset the station
        self.station.active(False)
        self.station.active(True)

        self.loop = get_event_loop()

        self.loop.create_task(self.check_mode())

    async def check_mode(self):
        await self.connect_async()

        if self.station.isconnected():
            self.loop.create_task(self.station_mode())
        else:
            self.loop.create_task(self.start_access_point())

    async def station_mode(self):
        while self.station.isconnected():
            await sleep_ms(CHECK_CONNECTED)

        self.station.disconnect()
        self.ip = NO_IP

        self.callback_connection_fail()

        self.loop.create_task(self.start_access_point())

    async def start_access_point(self):
        if not self.acess_point.active():
            self.acess_point.active(True)

            while not self.acess_point.active():
                await sleep_ms(CHECK_CONNECTED)

            self.ip = AP_IP

            # IP address, netmask, gateway, DNS
            self.acess_point.ifconfig((self.ip, SERVER_SUBNET, self.ip, self.ip))

            self.acess_point.config(essid=self.access_point_essid, authmode=AUTH_OPEN)
            print("> AP mode configured: {:s} ({:s})".format(self.access_point_essid, self.ip))

            self.callback_access_point_active()

    def connect(self):
        self.loop.create_task(self.connect_async())

    async def connect_async(self):
        credentials = Credentials().load()

        if credentials.is_valid() and credentials.essid != b"" and credentials.password != b"":
            hidden_pass = "*" * len(credentials.password)

            print("> Connecting to {:s}/{:s}".format(credentials.essid, hidden_pass))

            self.station.connect(credentials.essid, credentials.password)

            retry = 0

            while retry < MAX_WAIT_FOR_CONNECTION_CHECK and not self.station.isconnected():
                retry = retry + 1
                await sleep_ms(WAIT_FOR_CONNECTION_CHECK)

            if not self.station.isconnected():
                print("> Connection not successful!")

                self.station.disconnect()
                self.callback_connection_fail()
            else:
                self.ip = b"%s" % self.station.ifconfig()[0]

                Blink().flash_3_times_fast()

                await sleep_ms(WAIT_FOR_BLINK)

                credentials = Credentials().load()

                print("> Connected to {:s} with IP: {:s}".format(credentials.essid, self.ip))

                if self.acess_point.active():
                    # Set the IP address of the device with the one received from the router,
                    # so that the front-end app can get the new IP before the device is reset.
                    self.callback_set_station_ip()

                    await sleep_ms(WAIT_BEFORE_RESET)
                    reset()
                else:
                    self.callback_connection_success()

    def set_access_point_essid(self, access_point_essid):
        self.access_point_essid = access_point_essid

    def get_ssids(self):
        now = ticks_ms()

        if len(self.ssids) == 0 or ticks_diff(now, self.ssids_timestamp + SCAN_SSIDS_REFRESH) > 0:
            ssids = self.station.scan()
            self.ssids_timestamp = now
            self.ssids = []

            for ssid in ssids:
                self.ssids.append('"%s"' % ssid[0].decode("ascii"))

            self.ssids = list(set(self.ssids))
            self.ssids.sort()

        return b'{"ssids": [%s]}' % (",".join(self.ssids))