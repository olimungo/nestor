from machine import Pin
from uasyncio import get_event_loop, sleep_ms
from neopixel import NeoPixel
from clock import Clock
from spinner import Spinner
from settings import Settings
from credentials import Credentials

GPIO_BUTTON = const(16) #D0
GPIO_DATA = const(4) #D2
LEDS = const(59)

STATE_OFF = const(0)
STATE_CLOCK = const(1)
STATE_SPINNER = const(2)
STATE_IP = const(3)

READ_BUTTON_INTERVAL = const(100)
DISPLAY_IP_SEGMENT_DURATION = const(2000)
DISPLAY_IP_SEGMENT_CLEAR_DURATION = const(500)
SPINNER_RATE = const(120)

ORANGE = (255, 98, 0)
GREEN = (19, 215, 19)

DIGITS = [1, 15, 31, 45]

class Display:
    state = STATE_OFF
    get_time = None

    def __init__(self, ip):
        self.ip = ip.decode("ascii")

        settings = Settings().load()

        self.clock = Clock(settings.color)
        self.spinner = Spinner()

        self.leds_strip = NeoPixel(Pin(GPIO_DATA), LEDS)
        self.button = Pin(GPIO_BUTTON, Pin.IN)

        self.loop = get_event_loop()

    def off(self):
        if self.state != STATE_OFF:
            self.state = STATE_OFF

            self.stop()
            self.clear_all()

    def stop(self):
            self.spinner.stop()
            self.clock.stop()

    def display_spinner(self):
        if self.state != STATE_SPINNER:
            if self.state != STATE_IP:
                self.stop()

                credentials = Credentials().load()

                if credentials.is_valid() and credentials.essid != b"" and credentials.password != b"":
                    color = GREEN
                else:
                    color = ORANGE

                self.spinner.start(SPINNER_RATE, color)

            self.state = STATE_SPINNER

    def display_clock(self):
        if self.state != STATE_CLOCK:
            if self.state != STATE_IP:
                self.stop()
                self.clock.get_time = self.get_time
                self.clock.start()
                
            self.loop.create_task(self.read_button())
            self.state = STATE_CLOCK

    async def read_button(self):
        while True and self.state == STATE_CLOCK:
            if self.button.value():
                previous_state = self.state
                self.state = STATE_IP

                self.stop()

                await self.display_ip()

                if self.state == STATE_CLOCK or previous_state == STATE_CLOCK:
                    self.state = -1
                    self.display_clock()
                elif self.state == STATE_SPINNER or previous_state == STATE_SPINNER:
                    self.state = -1
                    self.display_spinner()
                else:
                    self.state = -1
                    self.off()

            await sleep_ms(READ_BUTTON_INTERVAL)

    async def display_ip(self):
        ip = self.ip.split(".")

        self.clock.clear_all()

        await self.dislay_ip_segment(ip[0])

        self.clock.clear_all()
        await sleep_ms(DISPLAY_IP_SEGMENT_CLEAR_DURATION)

        await self.dislay_ip_segment(ip[1])

        self.clock.clear_all()
        await sleep_ms(DISPLAY_IP_SEGMENT_CLEAR_DURATION)

        await self.dislay_ip_segment(ip[2])

        self.clock.clear_all()
        await sleep_ms(DISPLAY_IP_SEGMENT_CLEAR_DURATION)

        await self.dislay_ip_segment(ip[3])

    async def dislay_ip_segment(self, segment):
        self.update(2, 0, (0, 0, 0))
        self.update(3, 0, (0, 0, 0))
        self.update(4, 0, (0, 0, 0))

        position = 4

        while segment != "":
            number = int(segment[-1])
            segment = segment[:-1]
            self.update(position, number, GREEN)
            position -= 1

        self.leds_strip.write()

        await sleep_ms(DISPLAY_IP_SEGMENT_DURATION)

    def clear_all(self):
        self.leds_strip.fill((0, 0, 0))
        self.leds_strip.write()

    def update(self, position, value, rgb):
        leds = []
        start = DIGITS[position - 1]

        for i in range(start, start + 7 * 2):
            self.leds_strip[i] = (0, 0, 0)

        if value == 0: leds = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]
        elif value == 1: leds = [4, 5, 12, 13]
        elif value == 2: leds = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        elif value == 3: leds = [2, 3, 4, 5, 6, 7, 10, 11, 12, 13]
        elif value == 4: leds = [0, 1, 4, 5, 6, 7, 12, 13]
        elif value == 5: leds = [0, 1, 2, 3, 6, 7, 10, 11, 12, 13]
        elif value == 6: leds = [0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13]
        elif value == 7: leds = [2, 3, 4, 5, 12, 13]
        elif value == 8: leds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        elif value == 9: leds = [0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13]

        for led in leds:
            self.leds_strip[led + start] = rgb
