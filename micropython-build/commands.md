### Create the image

docker build -f Dockerfile.base -t micropython-base .
docker build -t micropython .

### Run container

docker run -d --name=micropython micropython

### Enter the previously created container

docker exec -it micropython /bin/bash -l

### Retrieve firmware

docker cp micropython:/micropython/ports/esp8266/build-GENERIC/firmware-combined.bin ..


### FAILED BUILD

cd /esp-open-sdk/crosstool-NG/.build/tarballs
wget https://github.com/libexpat/libexpat/releases/download/R_2_1_0/expat-2.1.0.tar.gz

docker build -f Dockerfile.micropython -t micropython .

docker build -t micropython-base -f Dockerfile.base .
docker build -t micropython-sources -f Dockerfile.sources .
docker build -t micropython-tarballs -f Dockerfile.tarballs .
