from gc import collect, mem_free
from uasyncio import get_event_loop
from connectivity_manager import ConnectivityManager

def settings_values(params):
    result = (
        b'{"ip": "%s", "netId": "%s",  "essid": "%s", "state": "%s,%s", "type": "%s"}'
        % ("1.2.3.4", "99", "", "ON", "OFF", "DOUBLE-SWITCH")
    )

    return result

url_routes = {
    b"/settings/values": settings_values
}

conman = ConnectivityManager(url_routes)

collect()
print("\n> >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
print("> Free mem after all classes created: {}".format(mem_free()))
print("> >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n")

loop = get_event_loop()
loop.run_forever()
loop.close()

