from gc import callbacks
from ubinascii import hexlify
from umqtt.simple import MQTTClient
from machine import unique_id
from uasyncio import get_event_loop, sleep_ms
from tags import Tags

SEND_STATE_INTERVAL = const(2000)
WAIT_FOR_MESSAGE = const(250)
WAIT_AFTER_ERROR = const(5000)

class MqttManager:
    def __init__(self, broker_ip, net_id, topics, topic_name, device_type):
        self.state_1 = "UNKNOWN"
        self.state_2 = None

        self.broker_ip = broker_ip
        self.net_id = net_id
        self.topics = topics
        self.commands_topic = b"commands/%s" % topic_name
        self.states_topic = b"states/%s" % topic_name
        self.logs_topic = b"logs/%s" % topic_name
        self.device_type = device_type

        self.loop = get_event_loop()
        self.messages = []

        print("> MQTT server up")

    def start(self):
        if self.task_check_for_message == None:
            connect_success = self.connect()
            
            self.task_check_for_message = self.loop.create_task(self.check_for_message(connect_success))

            print("> MQTT server running")

    def stop(self):
        if self.task_check_for_message != None:
            self.task_check_for_message.cancel()
            self.task_check_for_message = None

            print("> MQTT server stopped")

        if self.task_send_state != None:
            self.task_send_state.cancel()
            self.task_send_state = None

        if self.mqtt != None:
            self.mqtt.disconnect()
            self.mqtt = None

    async def check_for_message(self, connect_success):
        while not connect_success:
            await sleep_ms(WAIT_AFTER_ERROR)
            connect_success = self.connect()

        self.task_send_state = self.loop.create_task(self.send_state())

        while True:
            try:
                self.mqtt.check_msg()
                await sleep_ms(WAIT_FOR_MESSAGE)
            except Exception as e:
                print("> MQTT broker connect error: {}".format(e))
                await sleep_ms(WAIT_AFTER_ERROR)

    async def send_state(self):
        while True:
            try:
                self.publish_state()
                await sleep_ms(SEND_STATE_INTERVAL)
            except Exception as e:
                print("> MQTT broker publish_state error: {}".format(e))
                await sleep_ms(WAIT_AFTER_ERROR)

    def connect(self):
        try:
            client_id = hexlify(unique_id())

            self.mqtt = MQTTClient(client_id, self.broker_ip)
            self.mqtt.set_callback(self.message_received)
            self.mqtt.connect()

            print("> MQTT client connected to broker: {}".format(self.broker_ip))

            self.set_state(self.state_1, self.state_2)

            if self.message_1 and self.message_2:
                self.mqtt.subscribe((b"%s/%sa" % (self.commands_topic, self.net_id)))
                self.mqtt.subscribe((b"%s/%sb" % (self.commands_topic, self.net_id)))
            else:
                self.mqtt.subscribe((b"%s/%s" % (self.commands_topic, self.net_id)))

            return True
        except Exception as e:
            self.mqtt = None

            print("> MQTT broker connect error: {}".format(e))

            return False

    def message_received(self, topic, message):
        callback = self.topics.get(topic.encode('ascii'), None)

        if callback != None:
            callback(topic, message)

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

        self.publish_state()

    def publish_state(self):
        if self.task_send_state != None:
            try:
                if self.message_1 and self.message_2:
                    self.mqtt.publish(b"%s/%sa" % (self.states_topic, self.mdns.net_id), self.message_1)
                    self.mqtt.publish(b"%s/%sb" % (self.states_topic, self.mdns.net_id), self.message_2)
                else:
                    self.mqtt.publish(b"%s/%s" % (self.states_topic, self.mdns.net_id), self.message_1)
            except Exception as e:
                print("> MQTT broker publish_state error: {}".format(e))

    def log(self, message):
        if self.task_send_state != None:
            try:
                self.mqtt.publish(b"%s/%s" % (self.logs_topic, self.mdns.net_id), message)
            except Exception as e:
                print("> MQTT broker log error: {}".format(e))

    def set_net_id(self, net_id):
        self.net_id = net_id

        # Restart server
        self.stop()
        self.start()
