from machine import Pin, ADC, reset, deepsleep
from time import sleep_ms

def rst():
    reset()

pin = Pin(2, Pin.OUT, Pin.PULL_DOWN) # D4
reed = ADC(0) # A0

pin.off()

print('Im awake, but Im going to sleep')
sleep_ms(10000)

deepsleep()

while True:
    pin.off()
    sleep_ms(500)

    print(reed.read())

    pin.on()
    sleep_ms(500)