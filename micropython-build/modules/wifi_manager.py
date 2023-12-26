from machine import reset
from network import WLAN, STA_IF, AP_IF, AUTH_OPEN
from uasyncio import get_event_loop, sleep_ms
from ubinascii import hexlify
from blink import Blink
from time import ticks_ms, ticks_diff
from credentials import Credentials

NO_IP = b"0.0.0.0"
AP_IP = b"1.2.3.4"
NO_MAC = b"00:00:00:00:00:00"
SERVER_SUBNET = "255.255.255.0"
MAX_WAIT_FOR_CONNECTION_CHECK = const(10)
WAIT_FOR_CONNECTION_CHECK = const(1000)
WAIT_BEFORE_RESET = const(15000)
SCAN_SSIDS_REFRESH = const(30000)
CHECK_CONNECTED = const(250)
WAIT_FOR_BLINK = const(1000)

class WifiManager:
    ip = NO_IP
    mac = NO_MAC
    ssids = []
    ssids_timestamp = 0

    def __init__(self, public_id, callback_connection_success, callback_connection_fail, callback_access_point_active, callback_set_station_ip):
        self.station = WLAN(STA_IF)
        self.access_point = WLAN(AP_IF)
        self.public_id = public_id
        self.callback_connection_success = callback_connection_success
        self.callback_connection_fail = callback_connection_fail
        self.callback_access_point_active = callback_access_point_active
        self.callback_set_station_ip = callback_set_station_ip

        # Make sure that AP is not active
        self.access_point.active(False)

        # Reset the station
        self.station.active(False)
        self.station.active(True)

        self.station.config(dhcp_hostname=self.public_id)

        self.mac = self.get_mac_address()

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
        if not self.access_point.active():
            self.access_point.active(True)

            while not self.access_point.active():
                await sleep_ms(CHECK_CONNECTED)

            self.ip = AP_IP

            # IP address, netmask, gateway, DNS
            self.access_point.ifconfig((self.ip, SERVER_SUBNET, self.ip, self.ip))
            self.access_point.config(essid=self.public_id, authmode=AUTH_OPEN)
            
            print("> AP mode configured: {:s} ({:s})".format(self.public_id, self.ip))

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

                if self.access_point.active():
                    # Set the IP address of the device with the one received from the router,
                    # so that the front-end app can get the new IP before the device is reset.
                    self.callback_set_station_ip()

                    await sleep_ms(WAIT_BEFORE_RESET)
                    reset()
                else:
                    self.callback_connection_success()

    def get_ssids(self):
        now = ticks_ms()

        if len(self.ssids) == 0 or ticks_diff(now, self.ssids_timestamp + SCAN_SSIDS_REFRESH) > 0:
            ssids = self.station.scan()
            self.ssids_timestamp = now
            self.ssids = []

            for ssid in ssids:
                ssid_ascii = ssid[0].decode("ascii")

                if ssid_ascii != "":
                   self.ssids.append(ssid_ascii)
            
            self.ssids = list(set(self.ssids))
            self.ssids.sort(key=str.lower)

        import json
        return b'{"ssids": %s}' % json.dumps(self.ssids)
    
    def get_mac_address(self):
        mac = self.station.config('mac')
        return hexlify(mac, ':').upper()