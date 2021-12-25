from ubinascii import hexlify
from umqtt.simple import MQTTClient
from machine import unique_id
from uasyncio import get_event_loop, sleep_ms
from network import WLAN, STA_IF
from tags import Tags

WAIT_FOR_MDNS = const(1000)
WAIT_BETWEEN_CONNECT = const(10000)
WAIT_FOR_MESSAGE = const(250)
MQTT_STATUS_INTERVAL = const(2000)

class MqttManager:
    message = ""
    messages = []
    state_1 = "UNKNOWN"
    state_2 = None

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

            while not self.connected and self.mdns.connected:
                await sleep_ms(WAIT_BETWEEN_CONNECT)

                if self.mdns.connected:
                    await self.connect()

                if self.connected:
                    print("> MQTT client connected to {}".format(self.broker_name.decode('ascii')))

                    self.set_state(self.state_1, self.state_2)

                    if self.message_1 and self.message_2:
                        self.mqtt.subscribe((b"%s/%sa" % (self.commands_topic, self.mdns.net_id)))
                        self.mqtt.subscribe((b"%s/%sb" % (self.commands_topic, self.mdns.net_id)))
                    else:
                        self.mqtt.subscribe((b"%s/%s" % (self.commands_topic, self.mdns.net_id)))

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
                print("> MQTT broker IP: %s" % broker_ip)

                self.mqtt = MQTTClient(client_id, broker_ip)
                self.mqtt.set_callback(self.message_received)
                self.mqtt.connect()

                self.connected = True

                self.log(b"IP assigned: %s" % (self.sta_if.ifconfig()[0]))
            else:
                print("> MQTT broker '{}' not reachable!".format(self.broker_name.decode('ascii')))
        except Exception as e:
            print("> MQTT broker connect error: {}".format(e))

    def check_msg(self):
        try:
            self.mqtt.check_msg()
        except Exception as e:
            self.connected = False

    def message_received(self, topic, message):
        self.messages.append({b"topic": topic, b"message": message})

    async def send_state(self):
        while True:
            self.publish_message()
            await sleep_ms(MQTT_STATUS_INTERVAL)

    def set_state(self, state_1, state_2=None):
        tags = Tags().load()
        tags_utf8 = []
        self.state_1 = state_1
        self.state_2 = state_2

        for tag in tags.tags:
            tags_utf8.append("\"%s\"" % (tag.decode('utf-8')))

        self.message_1 = b'{"ip": "%s", "type": "%s", "state": "%s", "tags": [%s] }' % (
            self.sta_if.ifconfig()[0],
            self.device_type,
            state_1,
            ",".join(tags_utf8)
        )

        if state_2:
            self.message_2 = b'{"ip": "%s", "type": "%s", "state": "%s", "tags": [%s] }' % (
                self.sta_if.ifconfig()[0],
                self.device_type,
                state_2,
                ",".join(tags_utf8)
            )
        else:
            self.message_2 = None

        self.publish_message()

    def publish_message(self):
        if self.connected:
            try:
                if self.message_1 and self.message_2:
                    self.mqtt.publish(b"%s/%sa" % (self.states_topic, self.mdns.net_id), self.message_1)
                    self.mqtt.publish(b"%s/%sb" % (self.states_topic, self.mdns.net_id), self.message_2)
                else:
                    self.mqtt.publish(b"%s/%s" % (self.states_topic, self.mdns.net_id), self.message_1)
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
