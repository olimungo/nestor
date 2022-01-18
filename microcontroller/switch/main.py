from uasyncio import get_event_loop, sleep_ms
from machine import reset, Pin
from time import sleep
from gc import collect, mem_free
from network import WLAN, STA_IF, AP_IF
from re import match
from wifi_manager import WifiManager
from http_server import HttpServer
from mdns_server import mDnsServer
from mqtt_manager import MqttManager
from settings import Settings
from credentials import Credentials
from tags import Tags

PUBLIC_NAME = b"Switch"
BROKER_NAME = b"nestor.local"
# BROKER_NAME = b"deathstar.local"
MQTT_TOPIC_NAME = b"switches"
DEVICE_TYPE = b"SWITCH"
DOUBLE_SWITCH = False

CHECK_CONNECTED = const(250)
WAIT_BEFORE_RESET = const(10)
MQTT_CHECK_MESSAGE_INTERVAL = const(250)
MQTT_CHECK_CONNECTED_INTERVAL = const(1000)

PIN_SWITCH_A = const(5)  # D1
PIN_SWITCH_B = const(4)  # D2

class Main:
    def __init__(self):
        self.sta_if = WLAN(STA_IF)
        self.ap_if = WLAN(AP_IF)
        settings = Settings().load()

        url_routes = {
            b"/action/toggle-a": self.toggle_a,
            b"/action/toggle-b": self.toggle_b,
            b"/settings/values": self.settings_values
        }

        mqtt_topics = {
            b"add-tag": self.add_remove_tag,
            b"remove-tag": self.add_remove_tag,
            b"on": self.on_off,
            b"of": self.on_off,
        }

        self.wifi = WifiManager(b"%s-%s" % (PUBLIC_NAME, settings.net_id))
        self.mdns = mDnsServer(PUBLIC_NAME.lower(), settings.net_id)
        self.mqtt = MqttManager(mqtt_topics, self.mdns, BROKER_NAME, MQTT_TOPIC_NAME, DEVICE_TYPE)

        self.http = HttpServer(url_routes, self.wifi, self.mdns)

        self.switch_a = Pin(PIN_SWITCH_A, Pin.OUT)
        self.switch_b = Pin(PIN_SWITCH_B, Pin.OUT)

        self.switch_a.on() if settings.state_a == b"1" else self.switch_a.off()
        self.switch_b.on() if settings.state_b == b"1" else self.switch_b.off()

        self.loop = get_event_loop()
        self.loop.create_task(self.check_connected())
        self.loop.create_task(self.check_mqtt())
        self.loop.run_forever()
        self.loop.close()

    async def check_connected(self):
        while True:
            while not self.sta_if.isconnected() or self.ap_if.active():
                await sleep_ms(CHECK_CONNECTED)

            self.set_state()
        
            while self.sta_if.isconnected():
                await sleep_ms(CHECK_CONNECTED)

    async def check_mqtt(self):
        while True:
            while self.mqtt.connected:
                self.check_message_mqtt()

                await sleep_ms(MQTT_CHECK_MESSAGE_INTERVAL)

            while not self.mqtt.connected:
                await sleep_ms(MQTT_CHECK_CONNECTED_INTERVAL)

            self.set_state()

    def add_remove_tag(self, topic, message):
        tags = Tags().load()
        # TODO: check why the message is split. Are there many tags sent within 1 request?
        tag = message.split(b"/")[1]

        if match("add-tag", message):
            tags.append(tag)
        else:
            tags.remove(tag)

    def on_off(self, topic, message):
        settings = Settings().load()

        if match("on", message):
            action_a = self.switch_a.on
            action_b = self.switch_b.on
            state = b"1"
        else:
            action_a = self.switch_a.off
            action_b = self.switch_b.off
            state = b"0"

        if match(".*/.*b$", topic):
            print("> Turning relay 2 on")

            action_b()
            settings.state_b = state
        else:
            print("> Turning relay 1 on")

            action_a()
            settings.state_a = state

        settings.write()
        self.set_state()

    def check_message_mqtt(self):
        settings = Settings().load()

        try:
            mqtt_message = self.mqtt.check_messages()

        except Exception as e:
            print("> Main.check_message_mqtt exception: {}".format(e))

    def settings_values(self, params):
        credentials = Credentials().load()
        settings = Settings().load()

        essid = credentials.essid

        if not essid:
            essid = b""

        # Global type is SWITCH but the front-end has to know if it's a simple or double switch
        if DOUBLE_SWITCH:
            device_type = "DOUBLE-SWITCH"
        else:
            device_type = DEVICE_TYPE

        result = (
            b'{"ip": "%s", "netId": "%s",  "essid": "%s", "state": "%s,%s", "type": "%s"}'
            % (self.wifi.ip, settings.net_id, essid, settings.state_a, settings.state_b, device_type)
        )

        return result

    def toggle_a(self, params):
        action = params.get(b"action", None)
        settings = Settings().load()

        if action == b"on":
            self.switch_a.on()
            settings.state_a = b"1"
        else:
            self.switch_a.off()
            settings.state_a = b"0"

        settings.write()

    def toggle_b(self, params):
        action = params.get(b"action", None)
        settings = Settings().load()

        if action == b"on":
            self.switch_b.on()
            settings.state_b = b"1"
        else:
            self.switch_b.off()
            settings.state_b = b"0"

        settings.write()

    def set_state(self):
        settings = Settings().load()

        state_a = "ON" if settings.state_a == b"1" else "OFF"
        state_b = "ON" if settings.state_b == b"1" else "OFF"

        self.mqtt.set_state(state_a, state_b)

try:
    collect()
    print("Free mem: {}".format(mem_free()))

    main = Main()
except Exception as e:
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))
    sleep(WAIT_BEFORE_RESET)
    reset()
