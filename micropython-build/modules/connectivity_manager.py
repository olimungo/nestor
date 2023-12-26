from time import ticks_ms, ticks_diff
from uasyncio import get_event_loop, sleep_ms
from wifi_manager import WifiManager
from credentials import Credentials

PREVENT_AUTO_CONNECT_DELAY = const(15000)
WAIT_BETWEEN_AUTO_CONNECT = const(30000)
WAIT_BETWEEN_CONNECTIVITY_CHECK = const(1000)

class ConnectivityManager:
    http_activity = False
    http = None
    ntp = None
    mdns = None
    mqtt = None
    states = []
    http_config = None
    task_connect = None
    task_connect_async = None

    def __init__(self,
        public_name, broker_name, url_routes,
        mqtt_topic_name, mqtt_subscribe_topics, device_type,
        callback_connectivity_up=None, callback_connectivity_down=None,
        use_ntp=False, use_mdns=False, use_mqtt=False):

        self.public_name = public_name
        self.broker_name = broker_name
        self.url_routes = url_routes
        self.mqtt_topic_name = mqtt_topic_name
        self.mqtt_subscribe_topics = mqtt_subscribe_topics
        self.device_type = device_type
        self.callback_connectivity_up = callback_connectivity_up
        self.callback_connectivity_down = callback_connectivity_down
        self.use_ntp = use_ntp
        self.use_mdns = use_mdns
        self.use_mqtt = use_mqtt

        creds = Credentials().load()
        public_id = b"%s-%s" % (public_name, creds.net_id)

        self.wifi = WifiManager(public_id, self.wifi_connection_success, self.wifi_connection_fail, self.start_http_server, self.set_station_ip)

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

        credentials = Credentials().load()
        credentials.essid = essid
        credentials.password = password
        credentials.write()

        self.wifi.connect()

    async def connect_async(self):
        while True:
            await sleep_ms(WAIT_BETWEEN_AUTO_CONNECT)

            now = ticks_ms()
            last_http_activity = self.http.last_activity

            # Don't try to auto connect if there was an http activity recently
            if not last_http_activity or ticks_diff(now, last_http_activity + PREVENT_AUTO_CONNECT_DELAY) > 0:
                self.loop.create_task(self.wifi.connect_async())

    def set_net_id(self, net_id):
        creds = Credentials().load()
        creds.net_id = net_id
        creds.write()

        self.set_http_config(self.http_config)

        if self.mdns: self.mdns.set_net_id(creds.net_id)
        if self.mqtt: self.mqtt.set_net_id(creds.net_id)

    def wifi_connection_success(self):
        if self.task_connect_async:
            self.task_connect_async.cancel()
            self.task_connect_async = None

        self.start_mdns()
        self.start_mqtt()
        self.start_http_server()
        self.start_ntp()

        if self.callback_connectivity_up:
            self.callback_connectivity_up()

    def set_station_ip(self):
        self.set_http_config(self.http_config)

    def wifi_connection_fail(self):
        if self.ntp: self.ntp.stop()
        if self.mqtt: self.mqtt.stop()
        if self.mdns: self.mdns.stop()

        if self.callback_connectivity_down:
            self.callback_connectivity_down()

        if not self.task_connect_async:
            self.task_connect_async = self.loop.create_task(self.connect_async())

    def start_http_server(self):
        if not self.http:
            from http_server import HttpServer
            self.http = HttpServer(self.url_routes, self.connect, self.wifi.get_ssids, self.set_net_id)

            if self.http_config:
                self.set_http_config(self.http_config)

    def start_ntp(self):
        if self.use_ntp:
            if not self.ntp:
                from ntp_time import NtpTime
                self.ntp = NtpTime()

    def start_mdns(self):
        if self.use_mdns:
            if not self.mdns:
                from mdns_server import mDnsServer
                creds = Credentials().load()
                self.mdns = mDnsServer(self.public_name.lower(), creds.net_id, self.wifi.ip)

    def start_mqtt(self):
        if self.use_mqtt:
            try:
                if not self.mqtt:
                    creds = Credentials().load()
                    broker_ip = self.mdns.resolve_mdns_address(self.broker_name.decode('ascii'))

                    if broker_ip:
                        from mqtt_manager import MqttManager
                        broker_ip = "{}.{}.{}.{}".format(*broker_ip)
                        self.mqtt = MqttManager(broker_ip, creds.net_id, self.wifi.ip, self.mqtt_topic_name,
                            self.mqtt_subscribe_topics, self.device_type)

                        if self.state:
                            self.mqtt.set_state(self.wifi.ip, self.state)
            except Exception as e:
                print("> connectivity_manager.start_mqtt: {}".format(e))

    def set_http_config(self, http_config):
        creds = Credentials().load()

        http_config.update({b"ip" : self.wifi.ip, b"mac" : self.wifi.mac, b"netId": creds.net_id, b"type": self.device_type, b"state": self.state})

        self.http_config = http_config

        if self.http:
            self.http.set_config(http_config)

    def set_state(self, http_config, state):
        self.state = state

        self.set_http_config(http_config)

        if self.mqtt:
            self.mqtt.set_state(self.wifi.ip, state)

    def get_ip(self):
        return self.wifi.ip
    
    def get_time(self):
        if self.ntp:
            return self.ntp.get_time()
        else:
            return None

    def publish_mqtt_message(self, device, message):
        self.mqtt.publish_message(device, message)
