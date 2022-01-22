from http_request import get
from machine import RTC
from ntptime import settime
from uasyncio import get_event_loop, sleep_ms

WAIT_FOR_UPDATING_TIME = const(300000) # 5 minutes
WAIT_FOR_UPDATING_OFFSET = const(3600000) # 1 hour
WAIT_AFTER_ERROR_TIME = const(5000)
WAIT_AFTER_ERROR_OFFSET = const(1000)

class NtpTime:
    def __init__(self):
        self.offset_hour = 0
        self.offset_minute = 0

        self.task_time = None
        self.task_offset = None

        self.loop = get_event_loop()

        print("> NTP time up")

    def start(self):
        if self.task_time == None:
            print("> NTP time running")

            update_time_success = self.update_time()
            update_offset_success = self.update_offset()

            self.task_time = self.loop.create_task(self.update_time_async(update_time_success))
            self.task_offset = self.loop.create_task(self.update_offset_async(update_offset_success))

    def stop(self):
        if self.task_time != None:
            self.task_time.cancel()
            self.task_time = None
            self.task_offset.cancel()
            self.task_offset = None

            print("> NTP time stopped")

    def update_time(self):
        try:
            settime()
            print("> NTP time updated: {}".format(RTC().datetime()))

            return True
        except Exception as e:
            print("> NtpTime.update_time error: {}".format(e))
            return False  

    def update_offset(self):
        try:
            worldtime = get("http://worldtimeapi.org/api/ip")
            offset = worldtime["utc_offset"]

            self.offset_hour = int(offset[1:3])
            self.offset_minute = int(offset[4:6])

            if offset[:1] == "-":
                self.offset_hour = -self.offset_hour

            print("> Time offset retrieved: {}h{}m".format(self.offset_hour, self.offset_minute))

            return True
        except Exception as e:
            print("> NtpTime.get_offset error: {}".format(e))
            return False         

    async def update_time_async(self, update_success):
        await sleep_ms(WAIT_FOR_UPDATING_TIME) if update_success else await sleep_ms(WAIT_AFTER_ERROR_TIME)

        while True:
            await sleep_ms(WAIT_FOR_UPDATING_TIME) if self.update_time() else await sleep_ms(WAIT_AFTER_ERROR_TIME)

    async def update_offset_async(self, update_success):
        await sleep_ms(WAIT_FOR_UPDATING_OFFSET) if update_success else await sleep_ms(WAIT_AFTER_ERROR_OFFSET)

        while True:
            await sleep_ms(WAIT_FOR_UPDATING_OFFSET) if self.update_offset() else await sleep_ms(WAIT_AFTER_ERROR_OFFSET)

    def get_time(self):
        _, _, _, _, hour, minute, second, _ = RTC().datetime()

        hour += self.offset_hour
        minute += self.offset_minute

        if minute > 60:
            hour += 1
            minute -= 60

        if hour > 23:
            hour -= 24

        if hour < 0:
            hour += 24

        hour1 = int(hour / 10)
        hour2 = hour % 10
        minute1 = int(minute / 10)
        minute2 = minute % 10
        second1 = int(second / 10)
        second2 = second % 10

        return hour1, hour2, minute1, minute2, second1, second2
