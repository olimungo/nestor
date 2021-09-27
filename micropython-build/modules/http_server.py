from machine import reset
from uasyncio import get_event_loop, sleep_ms
from usocket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from uselect import poll, POLLIN
from ure import compile
from gc import collect
from credentials import Credentials
from settings import Settings

MAX_PACKET_SIZE = const(768)
HTTP_PORT = const(80)
IDLE_TIME_BETWEEN_CHECKS = const(100)

HEADER_OK = b"HTTP/1.1 200 OK\r\n\r\n"
HEADER_REDIRECT = b"HTTP/1.1 302 Found\r\nLocation: index.html\r\n\r\n"
HEADER_NO_CONTENT = b"HTTP/1.1 204 No Content\r\n\r\n"
HEADER_CONTENT = b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: %s\r\n\r\n%s"
HEADER_CONTENT_HTML = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
HEADER_CONTENT_CSS = b"HTTP/1.1 200 OK\r\nContent-Type: text/css\r\n\r\n"
HEADER_CONTENT_JS = b"HTTP/1.1 200 OK\r\nContent-Type: text/javascript\r\n\r\n"

class HttpServer:
    def __init__(self, routes, wifi, mdns):
        self.routes = routes
        self.wifi = wifi
        self.mdns = mdns

        self.credentials = Credentials().load()

        basic_routes = {
            b"/": b"./index.html",
            b"/index.html": b"./index.html",
            b"/settings.html": b"./settings.html",
            b"/style.css": b"./style.css",
            b"/common-scripts.js": b"./common-scripts.js",
            b"/index-scripts.js": b"./index-scripts.js",
            b"/settings-scripts.js": b"./settings-scripts.js",
            b"/favicon.ico": self.favicon,
            b"/settings/net-id": self.settings_net_id,
            b"/settings/ssids": self.get_ssids,
            b"/connect": self.connect,
            b"/settings/router-ip-received": self.router_ip_received,
        }

        for route in basic_routes:
            self.routes.update({route: basic_routes[route]})

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.bind(("", HTTP_PORT))
        self.sock.listen(5)
        
        self.poller = poll()
        self.poller.register(self.sock, POLLIN)

        self.loop = get_event_loop()
        self.loop.create_task(self.check_request())

        print("> HTTP server up and running")

    def split_request(self, request):
        method = ""
        path = ""
        queryStrings = {}
        params = {}

        if isinstance(request, bytes):
            request = request.decode('ascii')

        try:
            regex = compile("[\r\n]")
            lines = regex.split(request)
            firstLine = str(lines[0])
            method, url, _ = firstLine.split(" ")

            path = url

            if len(url.split("?")) == 2:
                path, queryString = url.split("?")
                queryStrings = queryString.split("&")

            for item in queryStrings:
                k, v = item.split("=")
                params[b"%s" % k] = b"%s" % v

        except:
            print("> Bad request: " + request)

        return method, path, params

    def redirect(self, client):
        print("> Send 302 Redirect")

        client.send(HEADER_REDIRECT)
        client.close()

    def send_page(self, client, page):
        print("> Send page {}".format(page.decode('ascii')))

        page_split = page.split(b".")
        ext = page_split[len(page_split) - 1]

        if ext == b"html":
            client.send(HEADER_CONTENT_HTML)
        elif ext == b"css":
            client.send(HEADER_CONTENT_CSS)
        elif ext == b"js":
            client.send(HEADER_CONTENT_JS)

        file = open(page, "rb")

        try:
            while True:
                data = file.readline()

                if data == b"":
                    break

                if data != b"\n":
                    client.write(data)
        except Exception as e:
            print("> HttpServer.send_page exception: {}".format(e))

        file.close()
        client.close()

    def call_route(self, client, route, params):
        # Call a function, which may or may not return a response
        response = route(params)

        if isinstance(response, tuple):
            body = response[0] or b""
            header = response[1]
        else:
            body = response or b""
            header = None

        if body:
            response = header or HEADER_CONTENT % (len(body), body)
        elif header:
            response = header
        else:
            response = HEADER_OK

        client.send(response)
        client.close()
    
    async def check_request(self):
        start = True

        while True:
            try:
                collect()

                polled_request = self.poller.poll(1)

                if polled_request:
                    client, _ = self.sock.accept()
                    request = client.recv(MAX_PACKET_SIZE)

                    if request:
                        method, path, params = self.split_request(request)

                        print("> Http: method => {} | path => {} | params => {}".format(method, path, params))

                        route = self.routes.get(path.encode('ascii'), None)

                        if type(route) is bytes:
                            # Expect a filename, so return content of file
                            self.send_page(client, route)
                        elif callable(route):
                            self.call_route(client, route, params)
                        else:
                            self.send_page(client, "/index.html")
            except Exception as e:
                print("> HttpServer.check_request exception: {}".format(e))
                # reset()

            await sleep_ms(IDLE_TIME_BETWEEN_CHECKS)

    def favicon(self, params):
        print("> NOT sending the favico :-)")

    def connect(self, params):
        credentials = Credentials().load()

        credentials.essid = params.get(b"essid", None)
        credentials.password = params.get(b"password", None)
        credentials.write()

        self.wifi.connect()

    def router_ip_received(self, params):
        # Reset the microcontroller to make sure that resources are freed as much as possible
        reset()

    def settings_net_id(self, params):
        settings = Settings().load()
        
        id = params.get(b"id", None)

        if id:
            settings.net_id = id
            settings.write()

            if self.mdns != None:
                self.mdns.set_net_id(id)

    def get_ssids(self, params):
        return self.wifi.get_ssids()
