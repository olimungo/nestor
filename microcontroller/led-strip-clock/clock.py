from machine import Pin, Timer, sleep
from uasyncio import get_event_loop, sleep_ms
from display import Display
from credentials import Credentials
import colors

GPIO_BUTTON = const(14) #D5
#GPIO_BUTTON = const(16) #D0 - for old versions of the LED strip clock, don't forget to also change below (no pull-up) + test when reading value

STATE_OFF = const(0)
STATE_CLOCK = const(1)
STATE_SPINNER = const(2)
STATE_IP = const(3)

READ_BUTTON_INTERVAL = const(100)
CLOCK_TICK_INTERVAL = const(250)
DISPLAY_IP_SEGMENT_DURATION = const(1500)
DISPLAY_IP_SEGMENT_CLEAR_DURATION = const(500)
SPINNER_RATE = const(120)

ORANGE = (255, 98, 0)
GREEN = (19, 215, 19)

class Clock:
    state = None
    get_time = STATE_OFF
    hour1 = hour2 = minute1 = minute2 = second = -1
    rgb = hex = hsl = None
    timer = Timer(-1)

    def __init__(self, get_ip, get_time, hex, size):
        self.get_ip = get_ip
        self.get_time = get_time
        self.set_color(hex)
        self.size = size

        self.display = Display(size)

        self.button = Pin(GPIO_BUTTON, Pin.IN, Pin.PULL_UP)
        #self.button = Pin(GPIO_BUTTON, Pin.IN) # for old versions of LED strip clock

        self.loop = get_event_loop()
        self.loop.create_task(self.read_button())

    def tick(self, timer=None):
        if self.get_time:
            self.hour1, self.hour2, self.minute1, self.minute2, _, self.second2 = self.get_time()

            if self.second2 % 2:
                dots = [(0, self.rgb), (1, self.rgb)]
            else:
                dots = []

            self.display.write(
                self.display.get_digit(self.hour1, self.rgb),
                self.display.get_digit(self.hour2, self.rgb),
                dots,
                self.display.get_digit(self.minute1, self.rgb),
                self.display.get_digit(self.minute2, self.rgb))

    def on(self):
        self.state = STATE_CLOCK
        self.display.spinner_off()
        self.hour1 = self.hour2 = self.minute1 = self.minute2 = self.second = -1
        self.timer.init(period=CLOCK_TICK_INTERVAL, mode=Timer.PERIODIC, callback=self.tick)

    def off(self):
        self.state = STATE_OFF
        self.timer.deinit()
        self.display.spinner_off()
        self.display.clear_all()

    def spinner_on(self):
        self.state = STATE_SPINNER
        self.timer.deinit()

        credentials = Credentials().load()

        if credentials.is_valid() and credentials.essid != b"" and credentials.password != b"":
            color = GREEN
        else:
            color = ORANGE

        self.display.spinner_on(color)

    def set_color(self, hex):
        if isinstance(hex, bytes):
            hex = hex.decode("ascii")

        self.hex = hex
        self.rgb = colors.hex_to_rgb(hex)
        self.hsl = colors.rgb_to_hsl(self.rgb)

    def set_brightness(self, l):
        h, s, _ = colors.rgb_to_hsl(self.rgb)
        self.hsl = (h, s, l)
        self.rgb = colors.hsl_to_rgb(self.hsl)
        self.hex = colors.rgb_to_hex(self.rgb)

    async def read_button(self):
        while True:
            # if self.button.value(): # for old versions of the LED strip clock
            if not self.button.value():
                state = self.state
                self.off()

                self.display_ip()

                self.state = state

                if self.state == STATE_CLOCK:
                    self.on()
                elif self.state == STATE_SPINNER:
                    self.spinner_on()
                else:
                    self.off()

            await sleep_ms(READ_BUTTON_INTERVAL)

    def display_ip(self):
        ip = f"{self.get_ip().decode('ascii'):s}".split(".")

        self.display_number(ip[0])

        self.display.clear_all()
        sleep(DISPLAY_IP_SEGMENT_CLEAR_DURATION)

        self.display_number(ip[1])

        self.display.clear_all()
        sleep(DISPLAY_IP_SEGMENT_CLEAR_DURATION)
        
        self.display_number(ip[2])

        self.display.clear_all()
        sleep(DISPLAY_IP_SEGMENT_CLEAR_DURATION)
        
        self.display_number(ip[3])

    def display_number(self, number):
        self.display.clear_all()

        position = 4

        digits = []

        while number != "":
            digit = int(number[-1])
            number = number[:-1]
            digits.append(self.display.get_digit(digit, ORANGE))
            position -= 1

        while position > 0:
            position -= 1
            digits.append([])

        self.display.write(digits[3], digits[2], [], digits[1], digits[0])

        sleep(DISPLAY_IP_SEGMENT_DURATION)