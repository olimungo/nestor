from gc import collect, mem_free
from version import get_version, get_version_date

collect()
print("\n> >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
print("> Micropython build: {} ({})".format(get_version(), get_version_date()))
print("> >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

print("\n> Free mem at start: {}\n".format(mem_free()))

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
