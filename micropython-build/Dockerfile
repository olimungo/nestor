ARG VERSION=v1.17

FROM registry.gitlab.com/janpoboril/micropython-docker-build/esp8266:$VERSION

WORKDIR /micropython/ports/esp8266

COPY modules/ modules/

RUN make