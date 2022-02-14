from binascii import hexlify
from umqtt.simple import MQTTClient
from machine import unique_id
from uasyncio import get_event_loop, sleep_ms
from tags import Tags

SEND_STATE_INTERVAL = const(2000)
WAIT_FOR_MESSAGE = const(100)
WAIT_AFTER_ERROR = const(5000)

class MqttManager:
    states = []
    messages = []
    task_check_for_connect = None
    task_send_state = None
    task_check_for_message = None
    connected = False

    def __init__(self, broker_ip, net_id, ip, topic_name, topics, device_type, count_devices=1):
        self.broker_ip = broker_ip
        self.net_id = net_id
        self.ip = ip
        self.topics = topics
        self.commands_topic = b"commands/%s" % topic_name
        self.states_topic = b"states/%s" % topic_name
        self.logs_topic = b"logs/%s" % topic_name
        self.device_type = device_type
        self.count_devices = count_devices

        self.loop = get_event_loop()
        self.messages = []

        print("> MQTT server up")

        self.start()

    def start(self):
        if self.task_check_for_message == None:
            self.connected = self.connect()
            
            self.task_check_for_connect = self.loop.create_task(self.check_for_connect())

    def stop(self):
        server_stopped = False

        if self.task_check_for_connect:
            self.task_check_for_connect.cancel()
            self.task_check_for_connect = None
            server_stopped = True

        if self.task_check_for_message:
            self.task_check_for_message.cancel()
            self.task_check_for_message = None
            server_stopped = True

        if self.task_send_state:
            self.task_send_state.cancel()
            self.task_send_state = None
            server_stopped = True

        if self.mqtt:
            self.mqtt.disconnect()
            self.mqtt = None
            server_stopped = True

        if server_stopped:
            print("> MQTT server stopped")

    async def check_for_connect(self):
        while not self.connected:
            await sleep_ms(WAIT_AFTER_ERROR)
            self.connected = self.connect()

        if self.count_devices > 1:
            for index in range(1, self.count_devices + 1):
                subscription = b"%s/%s.%s" % (self.commands_topic, self.net_id, index)
                self.mqtt.subscribe(subscription)
                print(f"> MQTT subscription to {subscription:s}")
        else:
            subscription = b"%s/%s" % (self.commands_topic, self.net_id)
            self.mqtt.subscribe(subscription)
            print(f"> MQTT subscription to {subscription:s}")
        
        self.set_state(self.ip, self.states)
        self.task_send_state = self.loop.create_task(self.send_state())
        self.task_check_for_message = self.loop.create_task(self.check_for_message())

        self.log(b"IP assigned to %s-%s: %s" % (self.device_type, self.net_id, self.ip))

    async def check_for_message(self):
        while True:
            try:
                self.mqtt.check_msg()
                await sleep_ms(WAIT_FOR_MESSAGE)
            except Exception as e:
                print("> MqttManager.check_for_message error: {}".format(e))
                self.loop.create_task(self.handle_error())
                await sleep_ms(WAIT_AFTER_ERROR)

    async def send_state(self):
        while True:
            try:
                self.publish_state()
                await sleep_ms(SEND_STATE_INTERVAL)
            except Exception as e:
                print("> MqttManager.send_state error: {}".format(e))
                self.loop.create_task(self.handle_error())
                await sleep_ms(WAIT_AFTER_ERROR)

    def connect(self):
        try:
            client_id = hexlify(unique_id())

            self.mqtt = MQTTClient(client_id, self.broker_ip)
            self.mqtt.set_callback(self.message_received)
            self.mqtt.connect()

            print("> MQTT server running")

            print("> MQTT client connected to broker: {}".format(self.broker_ip))

            return True
        except Exception as e:
            self.mqtt = None
            print("> MqttManager.connect error: {}".format(e))

            return False

    def message_received(self, topic, message):
        tags = Tags().load()

        # message contains the mqtt command and can be just "up" or "add-tag/kitchen"
        mqtt_command = message.split(b"/")[0]

        if mqtt_command == b"add-tag":
            tag = message.split(b"/")[1]
            tags.append(tag)
            self.set_state(self.ip, self.states)
        elif mqtt_command == b"remove-tag":
            tag = message.split(b"/")[1]
            tags.remove(tag)
            self.set_state(self.ip, self.states)
        else:
            callback = self.topics.get(mqtt_command, None)

            if callback != None:
                callback(topic, message)

        # Check immediatly if another message is available
        self.mqtt.check_msg()

    def set_state(self, ip, states):
        tags = Tags().load()
        tags_utf8 = []
        self.ip = ip
        self.states = states
        self.ip = ip
        self.messages = []

        for tag in tags.tags:
            tags_utf8.append("\"%s\"" % (tag.decode('utf-8')))

        for state in states:
            self.messages.append(b'{"ip": "%s", "type": "%s", "state": "%s", "tags": [%s] }' % (
            self.ip,
            self.device_type,
            state,
            ",".join(tags_utf8)
        ))

        self.publish_state()

    def publish_state(self):
        if self.connected:
            try:
                if self.count_devices > 1:
                    for index in range(1, len(self.messages) + 1):
                        self.mqtt.publish(b"%s/%s.%s" % (self.states_topic, self.net_id, index), self.messages[index - 1])
                elif len(self.messages) > 0:
                    self.mqtt.publish(b"%s/%s" % (self.states_topic, self.net_id), self.messages[0])
            except Exception as e:
                print("> MqttManager.publish_state error: {}".format(e))

    def log(self, message):
        if self.connected:
            try:
                self.mqtt.publish(b"%s/%s" % (self.logs_topic, self.net_id), message)
                print(f"> MQTT log: {self.logs_topic:s}/{self.net_id:s} - {message:s}")
            except Exception as e:
                print("> MqttManager.log error: {}".format(e))

    def set_net_id(self, net_id):
        self.net_id = net_id

        # Restart server
        self.stop()
        self.start()

    async def handle_error(self):
        # Restart server
        self.stop()
        self.start()

        
        
