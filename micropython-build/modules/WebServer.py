import usocket as socket
import uselect
import ure

_HTTP_PORT = const(80)


class WebServer:
    def __init__(self, wifiManger):
        self.wifiManager = wifiManger
        self.webServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.webServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.webServer.bind(("", _HTTP_PORT))
        self.webServer.listen(1)

        self.poller = uselect.poll()
        self.poller.register(self.webServer, uselect.POLLIN)

    def _splitRequest(self, request):
        path = ""
        queryStrings = {}
        queryStringsArray = {}

        try:
            regex = ure.compile("[\r\n]")
            firstLine = str(regex.split(request)[0])
            _, url, _ = firstLine.split(" ")

            path = url

            if len(url.split("?")) == 2:
                path, queryString = url.split("?")
                queryStrings = queryString.split("&")

            for item in queryStrings:
                k, v = item.split("=")
                queryStringsArray[k] = v
        except:
            print("> Bad request: " + request)

        return path, queryStringsArray

    def ok(self, client):
        print("> Send empty OK response")

        client.send("HTTP/1.1 200 OK\r\n\r\n")
        client.close()

    def notFound(self, client):
        print("> Send Page not found")

        client.send(
            "HTTP/1.1 404 Not Found\r\n\r\nQUOD GRATIS ASSERITUR, GRATIS NEGATUR\r\n\r\n"
        )
        client.close()

    def redirectToIndex(self, client):
        print("> Send 302 Redirect")
        client.send("HTTP/1.1 302 Redirect\r\nLocation: index.html\r\n\r\n")
        client.close()

    def index(self, client, interpolate):
        print("> Send index page")

        file = open("index.html", "r")

        while True:
            data = file.readline()

            if data == "":
                break

            if data != "\n":
                for key in interpolate:
                    data = data.replace("%%{}%%".format(key), interpolate[key])

                client.write(data)

        file.close()

        # If in Captive Portal mode (ESP as an Access Point), do not close the client
        if self.wifiManager.isConnectedToStation():
            client.close()

    def poll(self):
        request = self.poller.poll(1)

        if request:
            client, addr = self.webServer.accept()
            request = client.recv(1024)
            path, queryStringsArray = self._splitRequest(request)

            return False, client, path, queryStringsArray
        else:
            return True, False, False, False
