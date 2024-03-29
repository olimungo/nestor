from uos import remove

FILE = "./settings.csv"

class Settings:
    def __init__(self, motor_reversed=b"0"):
        self.motor_reversed = motor_reversed

    def write(self):
        if self.is_valid():
            with open(FILE, "wb") as f:
                f.write(b",".join([self.motor_reversed]))

    def load(self):
        try:
            with open(FILE, "rb") as f:
                contents = f.read().split(b",")

            if len(contents) == 1:
                self.motor_reversed = contents

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

        self.motor_reversed = None

    def is_valid(self):
        if not isinstance(self.motor_reversed, bytes):
            return False

        return True
