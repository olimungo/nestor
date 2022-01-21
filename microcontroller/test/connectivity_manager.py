from uasyncio import get_event_loop, sleep_ms
from wifi_manager import WifiManager
from http_server import HttpServer
from ntp_time import NtpTime
from settings import Settings
from mdns_server import mDnsServer
from mqtt_manager import MqttManager

class ConnectivityManager:
    def __init__(self, public_name, broker_name, url_routes, mqtt_topic_name, mqtt_subscribe_topics, device_type, settings_values=None):
        self.http_activity = False
        self.http = None
        self.ntp = None
        self.mdns = None
        self.mqtt = None

        self.public_name = public_name
        self.broker_name = broker_name
        self.url_routes = url_routes
        self.mqtt_topic_name = mqtt_topic_name
        self.mqtt_subscribe_topics = mqtt_subscribe_topics
        self.device_type = device_type
        self.settings_values = settings_values

        settings = Settings().load()
        access_point_essid = b"%s-%s" % (public_name, settings.net_id)

        self.wifi = WifiManager(access_point_essid, self.wifi_connection_success, self.wifi_connection_fail, self.access_point_active)

        self.loop = get_event_loop()
        self.loop.create_task(self.check_connectivity())

    async def check_connectivity(self):
        while True:
            await sleep_ms(100)

    def set_settings_values(self, settings_values):
        settings = Settings().load()
        settings_values.update({b"ip" : self.wifi.ip.encode("ascii"), b"netId": settings.net_id})
        self.http.set_settings_values(settings_values)

    def set_net_id(self, net_id):
        settings = Settings().load()
        settings.net_id = net_id
        settings.write()

        self.set_settings_values(self.settings_values)

    def wifi_connection_success(self):
        self.start_ntp()
        self.start_mdns()
        self.start_mqtt()
        self.start_http_server()

    def wifi_connection_fail(self):
        if self.ntp: self.ntp.stop()
        if self.mdns: self.mdns.stop()
        if self.mqtt: self.mqtt.stop()
        if self.http: self.http.stop()

    def access_point_active(self):
        self.start_http_server()

    def start_http_server(self):
        if not self.http:
            self.http = HttpServer(self.url_routes, self.wifi.connect, self.wifi.get_ssids, self.set_net_id)

            if self.settings_values:
                self.set_settings_values(self.settings_values)

        self.http.start()

    def start_ntp(self):
        if not self.ntp:
            self.ntp = NtpTime()
        
        self.ntp.start()

    def start_mdns(self):
        if not self.mdns:
            settings = Settings().load()
            self.mdns = mDnsServer(self.public_name.lower(), settings.net_id)
        
        self.mdns.start()

    def start_mqtt(self):
        if not self.mqtt:
            settings = Settings().load()
            broker_ip = self.mdns.resolve_mdns_address(self.broker_name.decode('ascii'))

            if broker_ip:
                broker_ip = "{}.{}.{}.{}".format(*broker_ip)
                self.mqtt = MqttManager(broker_ip, settings.net_id, self.wifi.ip, self.mqtt_topic_name, self.mqtt_subscribe_topics, self.device_type)
        
        self.mqtt.start()

    def set_state(self, state_1, state_2=None):
        self.mqtt.set_state(state_1, state_2)

    # def http_activity(self):
    #     self.start_ntp = False
    #     self.start_mqtt = False
