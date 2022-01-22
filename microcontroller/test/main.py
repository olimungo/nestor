from gc import collect, mem_free
from time import sleep
from uasyncio import get_event_loop, sleep_ms
from connectivity_manager import ConnectivityManager
from tags import Tags

PUBLIC_NAME = b"Switch"
BROKER_NAME = b"nestor.local"
# BROKER_NAME = b"deathstar.local"
MQTT_TOPIC_NAME = b"switches"
DEVICE_TYPE = b"SWITCH"
DOUBLE_SWITCH = True

if DOUBLE_SWITCH:
    device_type = b"DOUBLE-SWITCH"
else:
    device_type = DEVICE_TYPE

def add_remove_tag(topic, message):
        print("add-tag")
        print(topic, message)

url_routes = {}
mqtt_subscribe_topics = {b"add-tag": add_remove_tag}
settings_values = {b"state": b"0,1", b"type": device_type}


conman = ConnectivityManager(PUBLIC_NAME, BROKER_NAME, url_routes, MQTT_TOPIC_NAME, mqtt_subscribe_topics, DEVICE_TYPE, settings_values)
# conman.set_settings_values({b"state": b"0,1", b"type": b"DOUBLE-SWITCH"})

collect()
print("\n> >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
print("> Free mem after all classes created: {}".format(mem_free()))
print("> >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n")

loop = get_event_loop()
loop.run_forever()
#loop.close()

