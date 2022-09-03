from machine import Pin
from time import sleep_ms

pin = Pin(2, Pin.OUT) # D4

while True:
    pin.off()
    sleep_ms(200)
    pin.on()
    sleep_ms(150)
    pin.off()
    sleep_ms(200)
    pin.on()
    sleep_ms(800)