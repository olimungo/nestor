FROM micropython-base

COPY modules/ /micropython/ports/esp8266/modules/

WORKDIR /micropython/ports/esp8266

RUN make
