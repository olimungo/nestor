FROM micropython-build

USER root

ENV PATH=/esp-open-sdk/xtensa-lx106-elf/bin:$PATH

COPY modules/ /micropython/ports/esp8266/modules/

WORKDIR /micropython/ports/esp8266

RUN make
