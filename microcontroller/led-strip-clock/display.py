from machine import Pin, Timer
from neopixel import NeoPixel

GPIO_DATA = const(4) #D2
SPINNER_INTERVAL_DURATION = const(150)

class Display:
    spinner_timer = Timer(-1)

    def __init__(self, size):
        self.size = size

        if self.size == b"LARGE":
            self.LEDS = 59
            self.DIGITS = [1, 15, 31, 45]
            self.DOTS = 29
            self.EFFECT_INIT = [(0, 1), (2, 3), (4, 5), (12, 13), (10, 11), (8, 9)]
        else:
            self.LEDS = 31
            self.DIGITS = [1, 8, 17, 24]
            self.DOTS = 15
            self.EFFECT_INIT = [0, 1, 2, 6, 5, 4]

        self.leds_strip = NeoPixel(Pin(GPIO_DATA), self.LEDS)
        self.clear_all()

    def clear_all(self):
        self.leds_strip.fill((0, 0, 0))
        self.leds_strip.write()

    def spinner_on(self, rgb):
        self.rgb = rgb
        self.effect = self.EFFECT_INIT.copy()

        self.spinner_timer.init(
            period=SPINNER_INTERVAL_DURATION, mode=Timer.PERIODIC, callback=self.spinner_tick
        )

    def spinner_off(self):
        self.spinner_timer.deinit()

    def spinner_tick(self, timer):
        if len(self.effect) == 0:
            self.effect = self.EFFECT_INIT.copy()

        current_step = self.effect.pop(0)

        self.leds_strip.fill((0, 0, 0))

        for start in self.DIGITS:
            if self.size == b"LARGE":
                self.leds_strip[start + current_step[0]] = self.rgb
                self.leds_strip[start + current_step[1]] = self.rgb
            else:
                self.leds_strip[start + current_step] = self.rgb

        self.leds_strip.write()

    def write(self, digit1, digit2, dots, digit3, digit4):
        self.leds_strip.fill((0, 0, 0))

        self.display_digit(1, digit1)
        self.display_digit(2, digit2)

        self.display_dots(dots)

        self.display_digit(3, digit3)
        self.display_digit(4, digit4)

        self.leds_strip.write()

    def display_digit(self, digit_position, digit):
        for led in digit:
            self.leds_strip[self.DIGITS[digit_position-1] + led[0]] = led[1]

    def display_dots(self, dots):
        for led in dots:
            self.leds_strip[self.DOTS + led[0]] = led[1]

    def get_digit(self, digit, rgb):
        if self.size == b"LARGE":
            if digit == 0: leds = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]
            elif digit == 1: leds = [4, 5, 12, 13]
            elif digit == 2: leds = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            elif digit == 3: leds = [2, 3, 4, 5, 6, 7, 10, 11, 12, 13]
            elif digit == 4: leds = [0, 1, 4, 5, 6, 7, 12, 13]
            elif digit == 5: leds = [0, 1, 2, 3, 6, 7, 10, 11, 12, 13]
            elif digit == 6: leds = [0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13]
            elif digit == 7: leds = [2, 3, 4, 5, 12, 13]
            elif digit == 8: leds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
            elif digit == 9: leds = [0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13]
        else:
            if digit == 0: leds = [0, 1, 2, 4, 5, 6]
            elif digit == 1: leds = [2, 6]
            elif digit == 2: leds = [1, 2, 3, 4, 5]
            elif digit == 3: leds = [1, 2, 3, 5, 6]
            elif digit == 4: leds = [0, 2, 3, 6]
            elif digit == 5: leds = [0, 1, 3, 5, 6]
            elif digit == 6: leds = [0, 1, 3, 4, 5, 6]
            elif digit == 7: leds = [1, 2, 6]
            elif digit == 8: leds = [0, 1, 2, 3, 4, 5, 6]
            elif digit == 9: leds = [0, 1, 2, 3, 5, 6]

        for index, led in enumerate(leds):
            leds[index] = (led, rgb)

        return leds
        