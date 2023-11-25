# Setup the Raspberry Pi and Mosquitto

## Burn Raspian to an SD-card

Download and install **Raspberry Pi Imager**: https://www.raspberrypi.org/downloads/

Allow ssh, set the mdns name to nestor.local and setup the Wifi network in the Raspberry Pi Imager settings.

Burn **Raspbian Lite** onto an SD card

## Setup the Pi

Insert the SD-card, connect the Pi physically to the Wifi router, boot it, then ssh it with the password **raspberry**

```bash
ssh pi@nestor.local
```

### Update the system

```bash
sudo apt-get update -y && \
sudo apt-get upgrade -y && \
sudo apt-get clean -y
```

#### Install drivers for the Wifi USB dongle (for Raspberry Pi 2)

```bash
sudo wget http://downloads.fars-robotics.net/wifi-drivers/install-wifi -O /usr/bin/install-wifi
sudo chmod +x /usr/bin/install-wifi
sudo install-wifi
```

After installation, reboot the Pi.

## Docker on the Pi

Install docker

Follow the installation instructions here: https://docs.docker.com/engine/install/debian/

:exclamation: To allow to run docker without sudo apply the following solution. :exclamation:

```bash
sudo usermod -aG docker pi
```

Then, log out from the Pi and log in back to refresh the session.

# Enable the Docker system service to start your containers on boot

With this in place, containers with a restart policy set to always or unless-stopped will be re-started automatically after a reboot.

```bash
sudo systemctl enable docker
```

# Portainer

```bash
docker run -d -p 8000:8000 -p 9443:9443 -p 81:9000 --name portainer \
    --restart=always \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v portainer_data:/data \
    portainer/portainer-ce:2.11.1
```
