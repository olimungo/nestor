from machine import Pin, Timer
from uasyncio import get_event_loop, sleep_ms
from neopixel import NeoPixel
import colors

from NtpTime import NtpTime

GPIO_DATA = const(4) #D2
GPIO_BUTTON = const(16) #D0
LEDS = const(59)
DOTS = const(29)
DIGITS = [1, 15, 31, 45]
EFFECT_INIT = [(0, 1), (2, 3), (4, 5), (12, 13), (10, 11), (8, 9)]

class Clock:
    hour1 = hour2 = minute1 = minute2 = second = -1
    rgb = hex = hsl = None
    tick_timer = Timer(-1)
    tick_button = Timer(-1)
    play_spinner_timer = Timer(-1)
    effect_to_play = effect_original = stop_effect_init = None

    def __init__(self, wifi, color="0000ff"):
        self.wifi = wifi
        self.leds_strip = NeoPixel(Pin(GPIO_DATA), LEDS)
        self.clear_all()

        self.time = NtpTime()

        self.set_color(color, False)

        self.loop = get_event_loop()

        self.button = Pin(GPIO_BUTTON, Pin.IN)
        self.tick_button.init(period=250, mode=Timer.PERIODIC, callback=self.read_button)

    def read_button(self, timer):
        if self.button.value():
            timer.deinit()
            self.stop()
            self.loop.create_task(self.display_ip())

    async def display_ip(self):
        ip = self.wifi.ip.split(".")

        self.clear_all()

        await self.dislay_ip_segment(ip[0])
        await self.dislay_ip_segment(ip[1])
        await self.dislay_ip_segment(ip[2])
        await self.dislay_ip_segment(ip[3])

        self.tick_button.init(period=250, mode=Timer.PERIODIC, callback=self.read_button)
        self.start()

    async def dislay_ip_segment(self, segment):
        self.update(2, 0, (0, 0, 0))
        self.update(3, 0, (0, 0, 0))
        self.update(4, 0, (0, 0, 0))

        position = 4

        while segment != "":
            number = int(segment[-1])
            segment = segment[:-1]
            self.update(position, number, (0, 255, 0))
            position -= 1

        self.leds_strip.write()

        await sleep_ms(2000)

    def clear_all(self):
        self.leds_strip.fill((0, 0, 0))
        self.leds_strip.write()

    def tick(self, timer=None):
        hour1, hour2, minute1, minute2, second1, second2 = self.time.get_time()
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

        for i in range(start, start + 7 * 2):
            self.leds_strip[i] = (0, 0, 0)

        if value == 0:
            leds = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]
        elif value == 1:
            leds = [4, 5, 12, 13]
        elif value == 2:
            leds = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        elif value == 3:
            leds = [2, 3, 4, 5, 6, 7, 10, 11, 12, 13]
        elif value == 4:
            leds = [0, 1, 4, 5, 6, 7, 12, 13]
        elif value == 5:
            leds = [0, 1, 2, 3, 6, 7, 10, 11, 12, 13]
        elif value == 6:
            leds = [0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13]
        elif value == 7:
            leds = [2, 3, 4, 5, 12, 13]
        elif value == 8:
            leds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        elif value == 9:
            leds = [0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13]

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