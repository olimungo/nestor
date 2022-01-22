from time import ticks_ms, ticks_diff
from uasyncio import get_event_loop, sleep_ms
from wifi_manager import WifiManager
from settings import Settings

PREVENT_AUTO_CONNECT_DELAY = const(15000)

class ConnectivityManager:
    def __init__(self, public_name, broker_name, url_routes, mqtt_topic_name, mqtt_subscribe_topics, device_type, settings_values=None):
        self.http_activity = False
        self.http = None
        self.ntp = None
        self.mdns = None
        self.mqtt = None
        self.task_connect = None
        self.task_connect_async = None

        self.public_name = public_name
        self.broker_name = broker_name
        self.url_routes = url_routes
        self.mqtt_topic_name = mqtt_topic_name
        self.mqtt_subscribe_topics = mqtt_subscribe_topics
        self.device_type = device_type
        self.settings_values = settings_values

        settings = Settings().load()
        access_point_essid = b"%s-%s" % (public_name, settings.net_id)

        self.wifi = WifiManager(access_point_essid, self.wifi_connection_success, self.wifi_connection_fail, self.access_point_active, self.set_station_ip)

        self.loop = get_event_loop()
        self.loop.create_task(self.check_connectivity())

    async def check_connectivity(self):
        while True:
            await sleep_ms(1000)

    def connect(self, essid, password):
        if self.task_connect_async:
            self.task_connect_async.cancel()
            self.task_connect_async = None

        if self.ntp: self.ntp.stop()
        if self.mqtt: self.mqtt.stop()
        if self.mdns: self.mdns.stop()

        self.wifi.connect(essid, password)

    async def connect_async(self):
        while True:
            await sleep_ms(20000)

            now = ticks_ms()
            last_http_activity = self.http.last_activity

            if not last_http_activity or ticks_diff(now, last_http_activity + PREVENT_AUTO_CONNECT_DELAY) > 0:
                self.loop.create_task(self.wifi.connect_async())

    def set_settings_values(self, settings_values):
        settings = Settings().load()
        settings_values.update({b"ip" : self.wifi.ip.encode("ascii"), b"netId": settings.net_id})
        print("> SETTINGS VALUES")
        print(settings_values)
        self.http.set_settings_values(settings_values)

    def set_net_id(self, net_id):
        settings = Settings().load()
        settings.net_id = net_id
        settings.write()

        self.set_settings_values(self.settings_values)

    def wifi_connection_success(self):
        if self.task_connect_async:
            self.task_connect_async.cancel()
            self.task_connect_async = None

        self.start_mdns()
        self.start_mqtt()
        self.start_http_server()
        self.start_ntp()

    def set_station_ip(self):
        self.set_settings_values(self.settings_values)

    def wifi_connection_fail(self):
        if self.ntp: self.ntp.stop()
        if self.mqtt: self.mqtt.stop()
        if self.mdns: self.mdns.stop()

        if not self.task_connect_async:
            self.task_connect_async = self.loop.create_task(self.connect_async())

    def access_point_active(self):
        self.start_http_server()

    def start_http_server(self):
        if not self.http:
            from http_server import HttpServer
            self.http = HttpServer(self.url_routes, self.connect, self.wifi.get_ssids, self.set_net_id)

            if self.settings_values:
                self.set_settings_values(self.settings_values)

        self.http.start()

    def start_ntp(self):
        if not self.ntp:
            from ntp_time import NtpTime
            self.ntp = NtpTime()
        
        self.ntp.start()

    def start_mdns(self):
        if not self.mdns:
            from mdns_server import mDnsServer
            settings = Settings().load()
            self.mdns = mDnsServer(self.public_name.lower(), settings.net_id)
        
        self.mdns.start()

    def start_mqtt(self):
        if not self.mqtt:
            settings = Settings().load()
            broker_ip = self.mdns.resolve_mdns_address(self.broker_name.decode('ascii'))

            if broker_ip:
                from mqtt_manager import MqttManager
                broker_ip = "{}.{}.{}.{}".format(*broker_ip)
                self.mqtt = MqttManager(broker_ip, settings.net_id, self.wifi.ip, self.mqtt_topic_name, self.mqtt_subscribe_topics, self.device_type)
        
                self.mqtt.start()

    def set_state(self, state_1, state_2=None):
        self.mqtt.set_state(state_1, state_2)

    # def http_activity(self):
    #     self.start_ntp = False
    #     self.start_mqtt = False
