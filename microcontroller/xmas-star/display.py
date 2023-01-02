from machine import Pin
from uasyncio import get_event_loop, sleep_ms
from neopixel import NeoPixel
import random
from settings import Settings

LEDS_COUNT = 51
PIN_DATA = const(5)  # D1 - GPIO5

MODE_OFF = const(0)
MODE_WHITE = const(1)
MODE_BLINK = const(2)
MODE_RED = const(3)
MODE_GREEN = const(4)
MODE_BLUE = const(5)
MODE_YELLOW = const(6)
MODE_RAINBOW = const(7)
MODE_FIRE = const(8)
MODE_SPARKLE = const(9)

RAINBOW_SPEED = const (25)
FIRE_SPEED = const (10)

class Display:
    def __init__(self):
        self.modes = [MODE_OFF, MODE_WHITE, MODE_BLINK, MODE_RED, MODE_GREEN, MODE_BLUE, MODE_YELLOW, MODE_RAINBOW, MODE_FIRE, MODE_SPARKLE]
        self.effect = None

        self.neopixels = NeoPixel(Pin(PIN_DATA), LEDS_COUNT)
        self.heat = [0 for _ in range(LEDS_COUNT)]

        self.clear()

        self.loop = get_event_loop()

        self.effect = self.loop.create_task(self.on())

    def next_mode(self, mode=None):
        if mode:
            current_mode = int(mode)
        else:
            settings = Settings().load()

            current_mode = int(settings.mode)
            current_mode = current_mode + 1

            if current_mode == len(self.modes):
                current_mode = 0

            settings.mode = b"%s" % current_mode
            settings.write()

        if self.effect:
            self.effect.cancel()
            self.effect = None

        if current_mode == MODE_OFF:
            self.effect = self.loop.create_task(self.off())
        elif current_mode == MODE_WHITE:
            self.fill((255, 255, 255))
        elif current_mode == MODE_BLINK:
            self.effect = self.loop.create_task(self.blink())
        elif current_mode == MODE_RED:
            self.fill((255, 0, 0))
        elif current_mode == MODE_GREEN:
            self.fill((0, 255, 0))
        elif current_mode == MODE_BLUE:
            self.fill((0, 0, 255))
        elif current_mode == MODE_YELLOW:
            self.fill((255, 255, 0))
        elif current_mode == MODE_RAINBOW:
            self.effect = self.loop.create_task(self.rainbow(RAINBOW_SPEED))
        elif current_mode == MODE_FIRE:
            self.effect = self.loop.create_task(self.fire())
        elif current_mode == MODE_SPARKLE:
            self.effect = self.loop.create_task(self.sparkle())

    def fill(self, rgb):
        for i in range(1, self.neopixels.n):
            self.neopixels[i] = rgb

        self.neopixels.write()

    def clear(self):
        self.neopixels.fill((0, 0, 0))
        self.neopixels.write()

    def color_wheel(self, wheel_pos):
        if wheel_pos < 85:
            return wheel_pos * 3, 255 - wheel_pos * 3, 0
        elif wheel_pos < 170:
            wheel_pos -= 85
            return 255 - wheel_pos * 3, 0, wheel_pos * 3
        else:
            wheel_pos -= 170
            return 0, wheel_pos * 3, 255 - wheel_pos * 3

    def set_pixel_heat_color(self, pixel, temperature):
        # Scale 'heat' down from 0-255 to 0-191
        t192 = round((temperature / 255) * 191)

        # Calculate ramp up from
        heatramp = t192 & 0x3F # 0..63
        heatramp <<= 2 # scale up to 0..252

        # Figure out which third of the spectrum we're in:
        if t192 > 0x80: # hottest
            self.neopixels[pixel] = (255, 255, heatramp)
        elif t192 > 0x40: # middle
            self.neopixels[pixel] = (255, heatramp, 0)
        else: # coolest
            self.neopixels[pixel] = (heatramp, 0, 0)

    async def rainbow(self, speed_delay):
        while True:
            for j in range(0, 256, 3):
                for i in range(1, self.neopixels.n):
                    r, g, b = self.color_wheel(int((i * 256 / self.neopixels.n) + j) & 255)
                    self.neopixels[i] = (r, g, b)

                self.neopixels.write()

                await sleep_ms(speed_delay)

    async def fire(self):
        cooling = 35
        sparking = 60

        while True:
            # Step 1. Cool down every cell a little
            for i in range(1, self.neopixels.n):
                max_random = (cooling * 10 / self.neopixels.n) + 2
                cooldown = int(random.getrandbits(8) / 256 * max_random)
        
                if cooldown > self.heat[i]:
                    self.heat[i] = 0
                else:
                    self.heat[i] = self.heat[i] - cooldown
        
            # Step 2. Heat from each cell drifts 'up' and diffuses a little
            for k in range(self.neopixels.n - 1, 2, -1):
                self.heat[k] = int((self.heat[k - 1] + self.heat[k - 2] + self.heat[k - 2]) / 3)

            # Step 3. Randomly ignite new 'sparks' near the bottom
            if random.getrandbits(8) < sparking:
                y = random.getrandbits(3) + 1
                rnd = int(random.getrandbits(7) / 128 * 95) + 100
                self.heat[y] = (self.heat[y] + rnd) & 255

            # Step 4. Convert heat to LED colors
            for j in range(1, self.neopixels.n):
                self.set_pixel_heat_color(j, self.heat[j])

            self.neopixels.write()

            await sleep_ms(FIRE_SPEED)

    async def sparkle(self):
        rgb = (0, 0, 0)
        sparkle_delay = 75
        speed_delay = 200

        while True:
            self.fill(rgb)

            pixel = {}
            
            for i in range(3):
                pixel[i] = int(random.getrandbits(8)/256 * (LEDS_COUNT - 1)) + 1
                self.neopixels[pixel[i]] = (255, 255, 255)

            self.neopixels.write()

            await sleep_ms(sparkle_delay)

            for i in range(3):
                self.neopixels[pixel[i]] = rgb
            
            self.neopixels.write()

            await sleep_ms(speed_delay)

    async def blink(self):
        while True:
            self.fill((0, 0, 0))

            await sleep_ms(2000)

            self.fill((255, 255, 255))

            await sleep_ms(2000)

    async def on(self):
        for i in range(1, self.neopixels.n):
            self.neopixels[i] = (0, 255, 0)
            self.neopixels.write()
            await sleep_ms(30)

        self.effect = None

        settings = Settings().load()
        self.next_mode(settings.mode)
    
    async def off(self):
        self.fill((255, 0, 0))

        for i in range(self.neopixels.n - 1, 0, -1):
            self.neopixels[i] = (0, 0, 0)
            self.neopixels.write()
            await sleep_ms(30)
