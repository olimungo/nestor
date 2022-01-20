from gc import collect, mem_free
from uasyncio import get_event_loop
from connectivity_manager import ConnectivityManager

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

url_routes = {}

# conman = ConnectivityManager(PUBLIC_NAME, url_routes, {b"state": b"0,1", b"type": device_type})
# conman.set_settings_values({b"state": b"0,1", b"type": b"DOUBLE-SWITCH"})

collect()
print("\n> >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
print("> Free mem after all classes created: {}".format(mem_free()))
print("> >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n")

loop = get_event_loop()
loop.run_forever()
loop.close()

