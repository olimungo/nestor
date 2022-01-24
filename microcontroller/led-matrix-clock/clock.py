from machine import Timer
from ntp_time import NtpTime
from display import fonts, Char, Column

class Clock:
    state = 0 # 0 = OFF / 1 = ON
    hour1 = hour2 = minute1 = minute2 = second = numBars = -1
    tickTimer = Timer(-1)
    refreshTimer = Timer(-1)
    cleanTimer = Timer(-1)
    get_time = None

    def __init__(self, board):
        self.board = board

        self.digit1 = Char(board, 2, fonts[0])
        self.digit2 = Char(board, 7, fonts[0])
        self.digit3 = Char(board, 14, fonts[0])
        self.digit4 = Char(board, 19, fonts[0])
        self.colon = Char(board, 12, fonts[10])
        self.bar1 = Column(board, 28, fonts[11][0])
        self.bar2 = Column(board, 29, fonts[11][0])

    def tick(self, timer=None):
        if self.get_time:
            hour1, hour2, minute1, minute2, second1, second2 = self.get_time()

            second = second1 * 10 + second2
            numBars = int(second / (60 / 9))  # 9 states = 8 lights + no light
            column = self.createbar(numBars)

            if second2 % 2:
                colon = fonts[10]
            else:
                colon = fonts[11]

            self.check_update(self.digit1, self.hour1, hour1, fonts[hour1])
            self.check_update(self.digit2, self.hour2, hour2, fonts[hour2])
            self.check_update(self.digit3, self.minute1, minute1, fonts[minute1])
            self.check_update(self.digit4, self.minute2, minute2, fonts[minute2])
            self.check_update(self.bar1, self.numBars, numBars, column)
            self.check_update(self.bar2, self.numBars, numBars, column)
            self.check_update(self.colon, self.second, second, colon)

            self.hour1 = hour1
            self.hour2 = hour2
            self.minute1 = minute1
            self.minute2 = minute2
            self.second = second
            self.numBars = numBars

    def refresh(self, timer=None):
        self.digit1.scroll()
        self.digit2.scroll()
        self.colon.show()
        self.digit3.scroll()
        self.digit4.scroll()

        if self.second == 0:
            self.bar1.scroll()
            self.bar2.scroll()
        else:
            self.bar1.show()
            self.bar2.show()

        self.board.show()

    def check_update(self, elem, prevVal, newVal, value):
        if prevVal != newVal:
            elem.setBuffer(value)

    def clean(self, timer=None):
        self.board.fill(0)
        self.board.show()

        self.hour1 = self.hour2 = -1
        self.minute1 = self.minute2 = -1
        self.second = -1

        self.digit1.clean()
        self.digit2.clean()
        self.colon.clean()
        self.digit3.clean()
        self.digit4.clean()
        self.bar1.clean()
        self.bar2.clean()

    def createbar(self, numBars):
        column = 0

        for i in range(numBars):
            column = (column << 1) + 1

        for i in range(0, 8 - numBars):
            column <<= 1

        return column

    def start(self):
        if self.state == 0: # OFF
            self.state = 1
            self.tick()
            self.refresh()
            self.tickTimer.init(period=250, mode=Timer.PERIODIC, callback=self.tick)
            self.refreshTimer.init(period=35, mode=Timer.PERIODIC, callback=self.refresh)

    def stop(self):
        if self.state == 1: # ON
            self.state = 0
            self.refreshTimer.deinit()
            self.tickTimer.deinit()

            self.cleanTimer.init(period=50, mode=Timer.ONE_SHOT, callback=self.clean)

