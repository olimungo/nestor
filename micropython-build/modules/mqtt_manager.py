from ubinascii import hexlify
from umqtt.simple import MQTTClient
from machine import unique_id
from uasyncio import get_event_loop, sleep_ms
from network import WLAN, STA_IF
from tags import Tags

WAIT_FOR_MDNS = const(1000)
WAIT_BETWEEN_CONNECT = const(5000)
WAIT_FOR_MESSAGE = const(250)
MQTT_STATUS_INTERVAL = const(2000)

class MqttManager:
    message = ""
    messages = []

    def __init__(self, mdns, broker_name, topic_name, device_type):
        self.sta_if = WLAN(STA_IF)
        self.mdns = mdns
        self.broker_name = broker_name
        self.commands_topic = b"commands/%s" % topic_name
        self.states_topic = b"states/%s" % topic_name
        self.logs_topic = b"logs/%s" % topic_name
        self.device_type = device_type

        self.loop = get_event_loop()
        self.connected = False
        self.messages = []

        self.loop.create_task(self.check_mdns())
        self.loop.create_task(self.send_state())

    async def check_mdns(self):
        while True:
            while not self.mdns.connected:
                await sleep_ms(WAIT_FOR_MDNS)

            while not self.connected:
                await self.connect()

            print("> MQTT client connected to {}".format(self.broker_name.decode('ascii')))

            self.set_state()

            while self.connected and self.mdns.connected:
                self.check_msg()
                await sleep_ms(WAIT_FOR_MESSAGE)

            print("> MQTT server down")
            self.connected = False

    async def connect(self):
        try:
            client_id = hexlify(unique_id())

            broker_name = self.broker_name.split(b".")

            if len(broker_name) == 2 and broker_name[1] == b"local":
                broker_ip = self.mdns.resolve_mdns_address(self.broker_name.decode('ascii'))

                if broker_ip != None:
                    broker_ip = "{}.{}.{}.{}".format(*broker_ip)
            else:
                broker_ip = self.broker_name

            if broker_ip != None:
                self.mqtt = MQTTClient(client_id, broker_ip)
                self.mqtt.set_callback(self.message_received)
                self.mqtt.connect()

                self.mqtt.subscribe((b"%s/%s" % (self.commands_topic, self.mdns.net_id)))

                self.connected = True

                self.log(b"IP assigned: %s" % (self.sta_if.ifconfig()[0]))
            else:
                print("> MQTT broker '{}' not reachable!".format(self.broker_name.decode('ascii')))
                await sleep_ms(WAIT_BETWEEN_CONNECT)
        except Exception as e:
            print("> MQTT broker connect error: {}".format(e))
            await sleep_ms(WAIT_BETWEEN_CONNECT)

    def check_msg(self):
        try:
            self.mqtt.check_msg()
        except Exception as e:
            self.connected = False

    def message_received(self, topic, message):
        self.messages.append(message)

    async def send_state(self):
        while True:
            self.publish_message()
            await sleep_ms(MQTT_STATUS_INTERVAL)

    def set_state(self, state="UNKNOWN"):
        tags = Tags().load()
        tags_utf8 = []

        for tag in tags.tags:
            tags_utf8.append("\"%s\"" % (tag.decode('utf-8')))

        self.message = b'{"ip": "%s", "type": "%s", "state": "%s", "tags": [%s] }' % (
            self.sta_if.ifconfig()[0],
            self.device_type,
            state,
            ",".join(tags_utf8)
        )

        self.publish_message()

    def publish_message(self):
        if self.connected:
            try:
                self.mqtt.publish(b"%s/%s" % (self.states_topic, self.mdns.net_id), self.message)
            except Exception as e:
                print("> MQTT broker publish_message error: {}".format(e))

    def log(self, message):
        if self.connected:
            try:
                self.mqtt.publish(b"%s/%s" % (self.logs_topic, self.mdns.net_id), message)
            except Exception as e:
                print("> MQTT broker log error: {}".format(e))

    def check_messages(self):
        if len(self.messages) > 0:
            # Return first elem of the array
            return self.messages.pop(-len(self.messages))

        return None
