from machine import Pin, SPI
# import network
# import uasyncio as asyncio
from display import fonts, Char, Column
from max7219 import Matrix8x8

# sta = network.WLAN(network.STA_IF)
# sta.active(True)
# sta.connect('SolarSystem', 'totototo')

CS = const(15)

spi = SPI(1, baudrate=10000000, polarity=1, phase=0)
board = Matrix8x8(spi, Pin(CS), 4)
board.brightness(0)
board.fill(1)
board.show()

# create tasks for the web server and the DNS server and then start them
# loop = asyncio.get_event_loop()
# loop.run_forever()
# loop.close()