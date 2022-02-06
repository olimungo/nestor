from socket import socket, getaddrinfo
from json import loads

MAX_PACKET_SIZE = const(100)

def get(url):
    _, _, host, path = url.split('/', 3)
    addr = getaddrinfo(host, 80)[0][-1]

    sock = socket()
    sock.settimeout(1000)

    sock.connect(addr)
    sock.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    
    result = b""
    while True:
        data = sock.recv(MAX_PACKET_SIZE)

        if data:
            result += data
        else:
            break

    sock.close()

    if result:
        result = result.split(b"\r\n\r\n")[1]
        result = loads(result)

        return result
    else:
        raise Exception("response received with empty content")