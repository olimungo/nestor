from uos import remove

FILE = "./settings.csv"

class Settings:
    def __init__(self, state_a=b"0", state_b=b"0", timer_a=b"0", timer_b=b"0"):
        self.state_a = state_a
        self.state_b = state_b
        self.timer_a = timer_a
        self.timer_b = timer_b

    def write(self):
        if self.is_valid():
            with open(FILE, "wb") as f:
                f.write(b",".join([self.state_a, self.state_b, self.timer_a, self.timer_b]))

    def load(self):
        try:
            with open(FILE, "rb") as f:
                contents = f.read().split(b",")

            if len(contents) == 4:
                self.state_a, self.state_b, self.timer_a, self.timer_b = contents

            if not self.is_valid():
                self.remove()
        except OSError as e:
            # File not found
            if e.args[0] == 2:
                self.write()

        return self

    def remove(self):
        try:
            remove(FILE)
        except OSError:
            pass

        self.state_a = self.state_b = self.timer_a = self.timer_b = None

    def is_valid(self):
        if not isinstance(self.state_a, bytes):
            return False
        if not isinstance(self.state_b, bytes):
            return False
        if not isinstance(self.timer_a, bytes):
            return False
        if not isinstance(self.timer_b, bytes):
            return False

        return True
