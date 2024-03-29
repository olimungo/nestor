from uos import remove

FILE = "./settings.csv"

class Settings:
    def __init__(self, state=b"0", timer=b"0"):
        self.state = state
        self.timer = timer

    def write(self):
        if self.is_valid():
            with open(FILE, "wb") as f:
                f.write(b",".join([self.state, self.timer]))

    def load(self):
        try:
            with open(FILE, "rb") as f:
                contents = f.read().split(b",")

            if len(contents) == 2:
                self.state, self.timer = contents

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

        self.state = self.timer = None

    def is_valid(self):
        if not isinstance(self.state, bytes):
            return False
        if not isinstance(self.timer, bytes):
            return False

        return True
