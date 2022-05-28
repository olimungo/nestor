from machine import Pin, Timer
from neopixel import NeoPixel
import colors

GPIO_DATA = const(4) #D2
LEDS = const(59)
#DOTS = const(29)
DOTS = const(15)
#DIGITS = [1, 15, 31, 45]
DIGITS = [1, 8, 17, 24]

class Clock:
    hour1 = hour2 = minute1 = minute2 = second = -1
    rgb = hex = hsl = None
    tick_timer = Timer(-1)
    get_time = None

    def __init__(self, color="0000ff"):
        self.leds_strip = NeoPixel(Pin(GPIO_DATA), LEDS)
        self.clear_all()

        self.set_color(color, False)

    def clear_all(self):
        self.leds_strip.fill((0, 0, 0))
        self.leds_strip.write()

    def tick(self, timer=None):
        if self.get_time:
            hour1, hour2, minute1, minute2, _, second2 = self.get_time()
            updated = False

            updated |= self.check_update(1, self.hour1, hour1)
            updated |= self.check_update(2, self.hour2, hour2)
            updated |= self.check_update(3, self.minute1, minute1)
            updated |= self.check_update(4, self.minute2, minute2)
            updated |= self.check_update_seconds(self.second, second2)

            if updated:
                self.leds_strip.write()

            self.hour1 = hour1
            self.hour2 = hour2
            self.minute1 = minute1
            self.minute2 = minute2
            self.second = second2

    def check_update(self, position, prevValue, newValue):
        if prevValue != newValue:
            self.update(position, newValue, self.rgb)
            return True

        return False

    def update(self, position, value, rgb):
        leds = []
        start = DIGITS[position - 1]

        # for i in range(start, start + 7 * 2):

        for i in range(start, start + 7):
            self.leds_strip[i] = (0, 0, 0)

        # if value == 0: leds = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]
        # elif value == 1: leds = [4, 5, 12, 13]
        # elif value == 2: leds = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        # elif value == 3: leds = [2, 3, 4, 5, 6, 7, 10, 11, 12, 13]
        # elif value == 4: leds = [0, 1, 4, 5, 6, 7, 12, 13]
        # elif value == 5: leds = [0, 1, 2, 3, 6, 7, 10, 11, 12, 13]
        # elif value == 6: leds = [0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13]
        # elif value == 7: leds = [2, 3, 4, 5, 12, 13]
        # elif value == 8: leds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        # elif value == 9: leds = [0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13]

        if value == 0: leds = [0, 1, 2, 4, 5, 6]
        elif value == 1: leds = [2, 6]
        elif value == 2: leds = [1, 2, 3, 4, 5]
        elif value == 3: leds = [1, 2, 3, 5, 6]
        elif value == 4: leds = [0, 2, 3, 6]
        elif value == 5: leds = [0, 1, 3, 5, 6]
        elif value == 6: leds = [0, 1, 3, 4, 5, 6]
        elif value == 7: leds = [1, 2, 6]
        elif value == 8: leds = [0, 1, 2, 3, 4, 5, 6]
        elif value == 9: leds = [0, 1, 2, 3, 6]

        for led in leds:
            self.leds_strip[led + start] = rgb

    def check_update_seconds(self, prevValue, newValue):
        if prevValue != newValue:
            if newValue % 2:
                value = self.rgb
            else:
                value = (0, 0, 0)

            self.leds_strip[DOTS] = self.leds_strip[DOTS + 1] = value

            return True

        return False

    def force_refresh(self):
        self.hour1 = self.hour2 = self.minute1 = self.minute2 = self.second = -1
        self.tick()

    def start(self):
        print("> Clock started")
        self.hour1 = self.hour2 = self.minute1 = self.minute2 = self.second = -1
        self.clear_all()
        self.tick()
        self.tick_timer.init(period=250, mode=Timer.PERIODIC, callback=self.tick)

    def stop(self):
        self.tick_timer.deinit()

    def set_color(self, hex, no_refresh=True):
        if isinstance(hex, bytes):
            hex = hex.decode("ascii")

        self.hex = hex
        self.rgb = colors.hex_to_rgb(hex)
        self.hsl = colors.rgb_to_hsl(self.rgb)

        if no_refresh:
            self.force_refresh()

    def set_brightness(self, l):
        h, s, _ = colors.rgb_to_hsl(self.rgb)
        self.hsl = (h, s, l)
        self.rgb = colors.hsl_to_rgb(self.hsl)
        self.hex = colors.rgb_to_hex(self.rgb)
        self.force_refresh()

    def off(self):
        self.tick_timer.deinit()
        self.clear_all()