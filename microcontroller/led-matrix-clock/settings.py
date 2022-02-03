from uos import remove

FILE = "./settings.csv"

class Settings:
    def __init__(self, net_id=b"0", state=b"1", brightness=b"1"):
        self.net_id = net_id
        self.state = state
        self.brightness = brightness

    def write(self):
        if self.is_valid():
            with open(FILE, "wb") as f:
                f.write(b",".join([self.net_id, self.state, self.brightness]))

    def load(self):
        try:
            with open(FILE, "rb") as f:
                contents = f.read().split(b",")

            if len(contents) == 3:
                self.net_id, self.state, self.brightness = contents

            if not self.is_valid():
                remove()
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

        self.net_id = self.state = self.brightness = None

    def is_valid(self):
        if not isinstance(self.net_id, bytes):
            return False
        if not isinstance(self.state, bytes):
            return False
        if not isinstance(self.brightness, bytes):
            return False

        return True
