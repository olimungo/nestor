## Run a container on development host and inject the host IP address

#### MacOS

```bash
sed -e "s/__HOST_IP__/$(ipconfig getifaddr en1)/g" docker-compose.yml \
    | docker-compose --file - up -d
```

#### Linux

```bash
sed -e "s/__HOST_IP__/$(hostname -I | awk '{print $1}')/g" docker-compose.yml \
    | docker-compose --file - up -d
```

## Open a shell in the container

```bash
docker exec -it nestor /bin/sh -l
```

## Build for Raspberry Pi

### Create builder

```bash
docker buildx create --name nestor-builder
docker buildx use nestor-builder
```

### Build and push to Docker Hub

```bash
docker buildx build --platform linux/arm/v7 -t olimungo/nestor:0.116 --push front-end
docker buildx build --platform linux/arm/v7 -t olimungo/mosquitto:0.1 --push back-end/mosquitto
docker buildx build --platform linux/arm/v7 -t olimungo/nestor-mqtt:0.6 --push back-end/mqtt
docker buildx build --platform linux/arm/v7 -t olimungo/nestor-websockets:0.5 --push back-end/websockets
```

### Download and run container on Pi and inject the host IP address

:exclamation: Make sure that a file log.txt exists locally on the Pi (touch log.txt). Otherwise the command below will create a directory and will throw an error. :exclamation:

:exclamation: Replace **wlan0** by **eth0** if the Pi is wired to your router instead of using the Wifi :exclamation:

```bash
docker run \
    -e "HOST_IP=$(ip -4 addr show wlan0 | grep -Po 'inet \K[\d.]+')" \
    -e "MQTT_BROKER=$(ip -4 addr show wlan0 | grep -Po 'inet \K[\d.]+')" \
    -p 80:8081 \
    -v ~/log.txt:/home/node/app/log.txt -d \
    --name=nestor \
    olimungo/nestor:alpine-0.99
```
