from machine import freq, Pin, ADC, reset
from esp import sleep_type, SLEEP_NONE
import webrepl

print(
    "\n\nJust Do It Yourself World Company Incorporated (c) from 2020 to eternity and beyond...\n"
)

freq(160000000)
sleep_type(SLEEP_NONE)

webrepl.start()

ir_sensor = ADC(0)


def rst():
    reset()

def ir_on():
    ir_power = Pin(16, Pin.OUT)
    ir_power.on()

def ir_off():
    ir_power = Pin(16, Pin.OUT)
    ir_power.off()

def ir_read():
    ir_sensor = ADC(0)
    print("> IR sensor read: {}".format(ir_sensor.read()))


