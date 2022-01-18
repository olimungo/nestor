from uasyncio import get_event_loop, sleep_ms
from wifi_manager import WifiManager
from http_server import HttpServer

class ConnectivityManager:
    def __init__(self, url_routes):
        self.start_mdns = False
        self.start_http = False
        self.start_ntp = False
        self.start_mqtt = False
        self.http_activity = False

        self.wifi = WifiManager(b"Clock-99", self.wifi_connection_success, self.wifi_connection_fail, self.access_point_active)
        self.http = HttpServer(url_routes, self.wifi.connect, self.wifi.get_ssids, None)

        self.loop = get_event_loop()

        self.loop.create_task(self.check_connectivity())

    async def check_connectivity(self):
        while True:
            await sleep_ms(500)

    def wifi_connection_success(self):
        print("Wifi OK")

    def wifi_connection_fail(self):
        print("Wifi FAIL")

    def access_point_active(self):
        self.http.start()

    def connectivity_up(self):
        self.start_http = True

    def http_up(self):
        self.start_ntp = True

    def mdns_up(self):
        self.start_mqtt = True

    # def http_activity(self):
    #     self.start_ntp = False
    #     self.start_mqtt = False
