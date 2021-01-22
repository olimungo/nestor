from time import sleep
from gc import collect, mem_free
from machine import (
    reset,
    deepsleep,
    reset_cause,
    PWRON_RESET,
    HARD_RESET,
    DEEPSLEEP_RESET,
    SOFT_RESET,
)
from time import sleep

from Settings import Settings
from Credentials import Credentials


class Main:
    def __init__(self):
        self.settings = Settings()
        self.credentials = Credentials()
        rst_cause = reset_cause()

        if rst_cause in [PWRON_RESET, SOFT_RESET]:
            self.power_on_reset_wkfl()
        elif rst_cause in [HARD_RESET]:
            self.hard_reset_wkfl()
        elif rst_cause == DEEPSLEEP_RESET:
            self.deepsleep_reset_wkfl()
        else:
            self.other_reset_wkfl()

    # Power on
    def power_on_reset_wkfl(self):
        print("> SOFT reset or POWER ON reset")

        from Display import Display

        self.display = Display()
        self.display_logo()

        self.check_credentials()

        from NetworkManager import NetworkManager

        self.networkManager = NetworkManager()
        self.networkManager.connect(self.credentials.essid, self.credentials.password)

        while not self.networkManager.isconnected():
            sleep(1)

        from NtpTime import NtpTime

        self.ntp = NtpTime()

        while not self.ntp.update_time():
            sleep(1)

        while not self.ntp.get_offset():
            sleep(1)

        hour1, hour2, minute1, minute2, _, _ = self.ntp.get_time()
        self.update_time_eco(hour1, hour2, minute1, minute2)

        # Update display takes a few secs, requery for current time in order to compute deepsleep duration
        _, _, _, _, second1, second2 = self.ntp.get_time()
        seconds = second1 * 10 + second2
        print("> Seconds to wake-up: {}".format(60 - 10 - seconds))
        deepsleep((60 - 10 - seconds) * 1000)

    # Reset from deep sleep after time-out or reset button pressed when IN deep sleep
    def deepsleep_reset_wkfl(self):
        print("> DEEPSLEEP reset")
        self.check_credentials()

        from Display import Display

        self.display = Display(False)
        # self.display_logo()
        # self.display.set_eco_mode(True)

        from NtpTime import NtpTime

        self.ntp = NtpTime()

        self.update_time()

    # Reset button pressed when NOT in deep sleep
    def hard_reset_wkfl(self):
        print("> HARD reset")
        self.display_access_point_icon()
        self.networkManager.start_access_point()
        self.start_http_server()

    def other_reset_wkfl(self):
        from machine import reset

        reset()

    def display_logo(self):
        pass
        from images import pepper_clock_icon, pepper_clock_icon_size

        self.display.display_image(
            pepper_clock_icon, pepper_clock_icon_size[0], pepper_clock_icon_size[1]
        )

    def display_no_wifi_icon(self):
        pass
        from images import no_wifi_icon, no_wifi_icon_size

        self.display.display_image(
            no_wifi_icon, no_wifi_icon_size[0], no_wifi_icon_size[1], True
        )

    def display_access_point_icon(self):
        pass
        from images import access_point_icon, access_point_icon_size

        self.display.display_image(
            access_point_icon, access_point_icon_size[0], access_point_icon_size[1]
        )

    def check_credentials(self):
        if self.credentials.load().is_valid():
            return

        self.display_no_wifi_icon()
        print("> Going to deep sleep...")
        deepsleep()

    def update_time(self):
        _, _, _, _, second1, second2 = self.ntp.get_time()
        seconds = second1 * 10 + second2

        print("> Seconds at wake-up: {}".format(seconds))

        if 60 - seconds > 10:
            deepsleep((60 - 10 - seconds) * 1000)

        if seconds != 0:
            sleep(60 - seconds)

        hour1, hour2, minute1, minute2, second1, second2 = self.ntp.get_time()

        self.update_time_eco(hour1, hour2, minute1, minute2)
        print(
            "{}{} : {}{} : {}{}".format(
                hour1, hour2, minute1, minute2, second1, second2
            )
        )

        # Update display takes a few secs, requery for current time in order to compute deepsleep duration
        _, _, _, _, second1, second2 = self.ntp.get_time()
        seconds = second1 * 10 + second2
        print("> Seconds to wake-up: {}".format(60 - 10 - seconds))
        deepsleep((60 - 10 - seconds) * 1000)

    def start_http_server(self):
        from HttpServer import HttpServer

        routes = {
            b"/": b"./index.html",
            b"/index.html": b"./index.html",
            b"/scripts.js": b"./scripts.js",
            b"/style.css": b"./style.css",
            b"/favicon.ico": self.favicon,
            b"/connect": self.connect,
            b"/settings/set-eco-mode": self.set_eco_mode,
            b"/settings/values": self.settings_values,
            b"/settings/shutdown-ap": self.shutdown_ap,
            b"/settings/connected": self.connected,
        }

        self.http = HttpServer(routes)
        print("> HTTP server up and running")

    def settings_values(self, _):
        essid = self.credentials.essid

        if not essid:
            essid = b""

        result = b'{"ecoMode": "%s", "essid": "%s"}' % (
            self.settings.load().eco_mode,
            essid,
        )

        return result

    def favicon(self, _):
        print("> NOT sending the favico :-)")

    def connect(self, params):
        self.credentials.essid = params.get(b"essid", None)
        self.credentials.password = params.get(b"password", None)
        self.credentials.write()

        self.networkManager.connect(self.credentials.essid, self.credentials.password)

    def shutdown_ap(self, params):
        deepsleep(1)

    def set_eco_mode(self, params):
        eco_mode = params.get(b"val", b"1")

        self.settings.eco_mode = eco_mode
        self.settings.write()

    def connected(self, params):
        if self.networkManager.isconnected():
            isconnected = b"1"
        else:
            isconnected = b"0"

        return b'{"connected": "%s"}' % (isconnected)

    def update_time_eco(self, hour1, hour2, minute1, minute2):
        from Display import COL_DIGITS

        self.display.fill_white()

        updated = self.display.draw_digit(COL_DIGITS[0], hour1, 0)
        updated = self.display.draw_digit(COL_DIGITS[1], hour2, 0) or updated
        updated = self.display.draw_digit(COL_DIGITS[2], minute1, 0) or updated
        updated = self.display.draw_digit(COL_DIGITS[3], minute2, 0) or updated
        updated = self.display.draw_dots(0, 0) or updated

        if updated:
            self.display.update()


try:
    collect()
    print("Free mem: {}".format(mem_free()))

    main = Main()
except Exception as e:
    print("> Software failure.\nGuru medidation #00000000003.00C06560")
    print("> {}".format(e))
    print("Free mem: {}".format(mem_free()))

    sleep(10)
    reset()
