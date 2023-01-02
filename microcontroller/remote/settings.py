from uos import remove

FILE = "./settings.csv"

class Settings:
    def __init__(self, command_a=b"", command_b=b""):
        self.command_a = command_a
        self.command_b = command_b

    def write(self):
        if self.is_valid():
            with open(FILE, "wb") as f:
                f.write(b",".join([self.command_a, self.command_b]))

    def load(self):
        try:
            with open(FILE, "rb") as f:
                content = f.read().split(b",")

            if len(content) == 2:
                self.command_a, self.command_b  = content

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

        self.command_a = self.command_b = None

    def is_valid(self):
        if not isinstance(self.command_a, bytes):
            return False
        if not isinstance(self.command_b, bytes):
            return False

        return True
