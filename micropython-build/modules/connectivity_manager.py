from time import ticks_ms, ticks_diff
from uasyncio import get_event_loop, sleep_ms
from wifi_manager import WifiManager
from settings import Settings

PREVENT_AUTO_CONNECT_DELAY = const(15000)
WAIT_BETWEEN_AUTO_CONNECT = const(30000)
WAIT_BETWEEN_CONNECTIVITY_CHECK = const(1000)

class ConnectivityManager:
    http_activity = False
    http = None
    ntp = None
    mdns = None
    mqtt = None
    state_1 = None
    state_2 = None
    http_config = None
    task_connect = None
    task_connect_async = None

    def __init__(self,
        public_name, broker_name, url_routes,
        mqtt_topic_name, mqtt_subscribe_topics,
        mqtt_device_type, http_device_type,
        use_ntp=False, use_mdns=False, use_mqtt=False):

        self.public_name = public_name
        self.broker_name = broker_name
        self.url_routes = url_routes
        self.mqtt_topic_name = mqtt_topic_name
        self.mqtt_subscribe_topics = mqtt_subscribe_topics
        self.mqtt_device_type = mqtt_device_type
        self.http_device_type =  http_device_type
        self.use_ntp = use_ntp
        self.use_mdns = use_mdns
        self.use_mqtt = use_mqtt

        settings = Settings().load()
        access_point_essid = b"%s-%s" % (public_name, settings.net_id)

        self.wifi = WifiManager(access_point_essid, self.wifi_connection_success, self.wifi_connection_fail, self.start_http_server, self.set_station_ip)

        self.loop = get_event_loop()
        self.loop.create_task(self.check_connectivity())

    async def check_connectivity(self):
        while True:
            await sleep_ms(WAIT_BETWEEN_CONNECTIVITY_CHECK)

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
            await sleep_ms(WAIT_BETWEEN_AUTO_CONNECT)

            now = ticks_ms()
            last_http_activity = self.http.last_activity

            # Don't try to auto connect if there was an http activity recently
            if not last_http_activity or ticks_diff(now, last_http_activity + PREVENT_AUTO_CONNECT_DELAY) > 0:
                self.loop.create_task(self.wifi.connect_async())

    def set_http_config(self, http_config):
        settings = Settings().load()

        if self.state_2:
            state = b"%s,%s" % (self.state_1, self.state_2)
        else:
            state = b"%s" % self.state_1

        http_config.update({b"ip" : self.wifi.ip.encode("ascii"), b"netId": settings.net_id, b"type": self.http_device_type, b"state": state})

        self.http_config = http_config

        if self.http:
            self.http.set_config(http_config)

    def set_net_id(self, net_id):
        settings = Settings().load()
        settings.net_id = net_id
        settings.write()

        self.set_http_config(self.http_config)

        if self.mdns: self.mdns.set_net_id(settings.net_id)
        if self.mqtt: self.mqtt.set_net_id(settings.net_id)

    def wifi_connection_success(self):
        if self.task_connect_async:
            self.task_connect_async.cancel()
            self.task_connect_async = None

        self.start_mdns()
        self.start_mqtt()
        self.start_http_server()
        self.start_ntp()

    def set_station_ip(self):
        self.set_http_config(self.http_config)

    def wifi_connection_fail(self):
        if self.ntp: self.ntp.stop()
        if self.mqtt: self.mqtt.stop()
        if self.mdns: self.mdns.stop()

        if not self.task_connect_async:
            self.task_connect_async = self.loop.create_task(self.connect_async())

    def start_http_server(self):
        if not self.http:
            from http_server import HttpServer
            self.http = HttpServer(self.url_routes, self.connect, self.wifi.get_ssids, self.set_net_id)

            if self.http_config:
                self.set_http_config(self.http_config)

        self.http.start()

    def start_ntp(self):
        if self.use_ntp:
            if not self.ntp:
                from ntp_time import NtpTime
                self.ntp = NtpTime()
            
            self.ntp.start()

    def start_mdns(self):
        if self.use_mdns:
            if not self.mdns:
                from mdns_server import mDnsServer
                settings = Settings().load()
                self.mdns = mDnsServer(self.public_name.lower(), settings.net_id)
        
            self.mdns.start()

    def start_mqtt(self):
        if self.use_mqtt:
            try:
                if not self.mqtt:
                    settings = Settings().load()
                    broker_ip = self.mdns.resolve_mdns_address(self.broker_name.decode('ascii'))

                    if broker_ip:
                        from mqtt_manager import MqttManager
                        broker_ip = "{}.{}.{}.{}".format(*broker_ip)
                        self.mqtt = MqttManager(broker_ip, settings.net_id, self.wifi.ip, self.mqtt_topic_name, self.mqtt_subscribe_topics, self.mqtt_device_type)

                        if self.state_1:
                            self.mqtt.set_state(self.state_1, self.state_2)
                
                self.mqtt.start()
            except Exception as e:
                print("> connectivity_manager.start_mqtt: {}".format(e))

    def set_state(self, state_1, state_2=None):
        self.state_1 = state_1
        self.state_2 = state_2

        if self.mqtt:
            self.mqtt.set_state(state_1, state_2)
