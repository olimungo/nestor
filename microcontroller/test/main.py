from gc import collect, mem_free
from time import sleep
from uasyncio import get_event_loop, sleep_ms
from connectivity_manager import ConnectivityManager
from tags import Tags

PUBLIC_NAME = b"Switch"
# BROKER_NAME = b"nestor.local"
BROKER_NAME = b"death-star.local"
MQTT_TOPIC_NAME = b"switches"
MQTT_DEVICE_TYPE = b"SWITCH"
HTTP_DEVICE_TYPE = b"DOUBLE-SWITCH"

def add_remove_tag(topic, message):
        print("add-tag")
        print(topic, message)

url_routes = {}
mqtt_subscribe_topics = {b"add-tag": add_remove_tag}
settings_values = {b"state": b"0,1"}

conman = ConnectivityManager(PUBLIC_NAME, BROKER_NAME, url_routes, MQTT_TOPIC_NAME, mqtt_subscribe_topics, MQTT_DEVICE_TYPE, HTTP_DEVICE_TYPE, settings_values,
    use_ntp=True, use_mdns=True, use_mqtt=True)

conman.set_state("ON" ,"OFF")

collect()
print("\n> >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
print("> Free mem after all classes created: {}".format(mem_free()))
print("> >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n")

loop = get_event_loop()
loop.run_forever()
loop.close()

