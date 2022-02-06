from uos import remove

FILE = "./creds.csv"

class Credentials:
    def __init__(self, essid=None, password=None, net_id=b"0"):
        self.essid = essid
        self.password = password
        self.net_id = net_id

    def write(self):
        if self.is_valid():
            with open(FILE, "wb") as f:
                f.write(b",".join([self.essid, self.password, self.net_id]))

    def load(self):
        try:
            with open(FILE, "rb") as f:
                contents = f.read().split(b",")

            if len(contents) == 3:
                self.essid, self.password, self.net_id = contents

            if not self.is_valid():
                self.remove()
        except OSError:
            pass

        return self

    def remove(self):        
        try:
            remove(FILE)
        except OSError:
            pass

        self.essid = self.password = None

    def is_valid(self):
        if not isinstance(self.essid, bytes):
            return False
        if not isinstance(self.password, bytes):
            return False
        if not isinstance(self.net_id, bytes):
            return False

        # Ensure credentials are not None or empty
        return all((self.essid, self.password))
