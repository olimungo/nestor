from machine import Pin, Timer

ESP_LED = const(2) # D4

class Blink:
    led = Pin(ESP_LED, Pin.OUT)
    # To make sure that the LED is in the state that we want when booting.
    # BTW, for the LED on D4, the methods are inversed:
    #    on() => turns the LED off
    #    off() => turns the LED on
    led.on()
    timer = Timer(-1)
    script = []
    current_action = []

    def flash(self, script=None):
        if script != None:
            self.script = script
            self.script.reverse()
            self.timer.deinit()

        if len(self.script) > 0 or len(self.current_action) > 0:
            if len(self.current_action) == 0:
                self.current_action = self.script.pop()
                self.current_action.reverse()
                delay = self.current_action.pop()
                self.led.on()
                self.timer.init(period=delay, mode=Timer.ONE_SHOT, callback=lambda l:self.flash())
            else:
                onDelay = self.current_action.pop()
                self.led.off()
                self.timer.init(period=onDelay, mode=Timer.ONE_SHOT, callback=lambda l:self.flash())
        else:
            self.led.on()

    def flash_3_times_fast(self):
        self.flash([[0, 100], [200, 100], [200, 100]])

    def flash_5_times_slow(self):
        self.flash([[0, 500], [400, 500], [400, 500], [400, 500], [400, 500]])
    
    def flash_once_slow(self):
        self.flash([[0, 1000]])
