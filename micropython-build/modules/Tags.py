FILE = "./tags.csv"


class Tags:
    def __init__(self):
        self.tags = []

    def write(self):
        with open(FILE, "wb") as file:
            if len(self.tags) > 0:
                file.write(b",".join(self.tags))
            else:
                file.write(b"")

    def load(self):
        try:
            with open(FILE, "rb") as file:
                content = file.read()

                if content != b"":
                    self.tags = content.split(b",")
                else:
                    self.tags = []

        except OSError as error:
            # File not found
            if error.args[0] == 2:
                self.write()

        return self

    def append(self, tag):
        self.tags.append(tag)
        self.write()

    def remove(self, tag):
        self.tags.remove(tag)
        self.write()
