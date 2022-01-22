from ubinascii import hexlify
from umqtt.simple import MQTTClient
from machine import unique_id
from uasyncio import get_event_loop, sleep_ms
from tags import Tags

SEND_STATE_INTERVAL = const(2000)
WAIT_FOR_MESSAGE = const(100)
WAIT_AFTER_ERROR = const(5000)
WAIT_A_BIT_BEFORE_LOGGING = const(1000)

class MqttManager:
    state_1 = "UNKNOWN"
    state_2 = None
    message_1 = None
    message_2 = None
    task_check_for_connect = None
    task_send_state = None
    task_check_for_message = None

    def __init__(self, broker_ip, net_id, ip, topic_name, topics, device_type):

        self.broker_ip = broker_ip
        self.net_id = net_id
        self.ip = ip
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
            
            self.task_check_for_connect = self.loop.create_task(self.check_for_connect(connect_success))

            print("> MQTT server running")

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

    async def check_for_connect(self, connect_success):
        while not connect_success:
            await sleep_ms(WAIT_AFTER_ERROR)
            connect_success = self.connect()

        if self.message_1 and self.message_2:
            self.mqtt.subscribe((b"%s/%sa" % (self.commands_topic, self.net_id)))
            self.mqtt.subscribe((b"%s/%sb" % (self.commands_topic, self.net_id)))
        else:
            self.mqtt.subscribe((b"%s/%s" % (self.commands_topic, self.net_id)))
        
        self.set_state(self.state_1, self.state_2)
        self.task_send_state = self.loop.create_task(self.send_state())
        self.task_check_for_message = self.loop.create_task(self.check_for_message())

        await sleep_ms(WAIT_A_BIT_BEFORE_LOGGING)

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

            print("> MQTT client connected to broker: {}".format(self.broker_ip))

            return True
        except Exception as e:
            self.mqtt = None

            print("> MqttManager.connect error: {}".format(e))

            return False

    def message_received(self, topic, message):
        # message contains the mqtt command and can be just "up" or "add-tag/kitchen"
        mqtt_command = message.split(b"/")[0]

        callback = self.topics.get(mqtt_command, None)

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
            self.ip,
            self.device_type,
            state_1,
            ",".join(tags_utf8)
        )

        if state_2:
            self.message_2 = b'{"ip": "%s", "type": "%s", "state": "%s", "tags": [%s] }' % (
                self.ip,
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
                    self.mqtt.publish(b"%s/%sa" % (self.states_topic, self.net_id), self.message_1)
                    self.mqtt.publish(b"%s/%sb" % (self.states_topic, self.net_id), self.message_2)
                else:
                    self.mqtt.publish(b"%s/%s" % (self.states_topic, self.net_id), self.message_1)
            except Exception as e:
                print("> MqttManager.publish_state error: {}".format(e))

    def log(self, message):
        if self.task_send_state != None:
            try:
                self.mqtt.publish(b"%s/%s" % (self.logs_topic, self.net_id), message)
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

        
        
