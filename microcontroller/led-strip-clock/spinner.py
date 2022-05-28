from machine import Pin, Timer
from math import floor
from neopixel import NeoPixel

GPIO_DATA = const(4) #D2
#LEDS = const(59)
LEDS = const(31)
#DIGITS = [1, 15, 31, 45]
DIGITS = [1, 8, 17, 24]
#EFFECT_INIT = [(0, 1), (2, 3), (4, 5), (12, 13), (10, 11), (8, 9)]
EFFECT_INIT = [0, 1, 2, 6, 5, 4]

class Spinner:
    rgb = hex = hsl = None
    tick_timer = Timer(-1)
    play_spinner_timer = Timer(-1)
    effect_to_play = effect_original = stop_effect_init = None

    def __init__(self):
        self.leds_strip = NeoPixel(Pin(GPIO_DATA), LEDS)
        self.clear_all()

    def clear_all(self):
        self.leds_strip.fill((0, 0, 0))
        self.leds_strip.write()

    def start(self, period, color):
        self.effect_original = EFFECT_INIT.copy()
        self.effect_to_play = []
        self.stop_effect_init = False
        self.effect_color = color

        self.clear_all()

        self.play_spinner_timer.init(
            period=period, mode=Timer.PERIODIC, callback=self.play_spinner_tick
        )

    def stop(self):
        self.stop_effect_init = True

    def play_spinner_tick(self, timer):
        if self.stop_effect_init:
            timer.deinit()
        else:
            if len(self.effect_to_play) == 0:
                self.effect_to_play = self.effect_original.copy()

            currentStep = self.effect_to_play.pop(0)

            for start in DIGITS:
                # for i in range(start, start + 7 * 2):
                #     self.leds_strip[i] = (0, 0, 0)

                # self.leds_strip[start + currentStep[0]] = self.effect_color
                # self.leds_strip[start + currentStep[1]] = self.effect_color

                for i in range(start, start + 7):
                    self.leds_strip[i] = (0, 0, 0)

                self.leds_strip[start + currentStep] = self.effect_color

            self.leds_strip.write()