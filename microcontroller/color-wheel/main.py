from uasyncio import get_event_loop, sleep_ms
from Blink import Blink

loop = get_event_loop()

b = Blink()
b.flash3TimesFast()

loop.run_forever()
loop.close()