from uos import remove

FILE = "./settings.csv"

class Settings:
    def __init__(self, mode=b"0"):
        self.mode = mode

    def write(self):
        if self.is_valid():
            with open(FILE, "wb") as f:
                f.write(b",".join([self.mode]))

    def load(self):
        try:
            with open(FILE, "rb") as f:
                content = f.read().split(b",")

            if len(content) == 1:
                self.mode = content[0]

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

        self.mode = None

    def is_valid(self):
        if not isinstance(self.mode, bytes):
            return False

        return True