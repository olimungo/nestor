from gc import collect, mem_free

collect()
print("\n\n\n> >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
print("> Free mem at start: {}".format(mem_free()))
print("> >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

from machine import freq
freq(160000000)

import webrepl
webrepl.start()

from esp import sleep_type, SLEEP_NONE
sleep_type(SLEEP_NONE)

print(
    "\n\nJust Do It Yourself World Company Incorporated (c) from 2020 to eternity and beyond...\n"
)

from machine import reset
def rst():
    reset()
