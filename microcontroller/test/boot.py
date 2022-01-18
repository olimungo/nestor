from gc import collect, mem_free

collect()
print("\n\n\n> >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
print("> Free mem at start: {}".format(mem_free()))
print("> >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

from machine import reset

# from machine import freq
from esp import sleep_type, SLEEP_NONE
import webrepl

print(
    "\n\nJust Do It Yourself World Company Incorporated (c) from 2020 to eternity and beyond...\n"
)

# freq(160000000)
sleep_type(SLEEP_NONE)

webrepl.start()

def rst():
    reset()
