# Docker on Mercure

## Installation

```bash
sudo apt update && sudo apt upgrade -y
curl -sSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

## Extend the files system

```bash
sudo raspi-config
```

Select "6 Advanced Options", then "A1 Expand Filesystem". \
Reboot.

## Mount an external USB drive

### Create the mount points on the local file system

```bash
sudo mkdir -p /mnt/external-media
sudo mkdir -p /mnt/backups
```

### Get the external disk name

```bash
lsblk
```

### Get the external drive unique Id

```bash
lsblk -fp
```

### Update the the fstab file

```bash
sudo vi /etc/fstab
```

### Adapt the following line while adding it to the fstab file

```
UUID=__unique_drive_id__ /mnt/external-media  ext4  defaults,nofail  0  2
```

### Actually mount the drive

```bash
sudo mount -a
systemctl daemon-reload
```

### Allow Samba to write to the mounted folders

```bash
sudo chown -R $USER:$USER /mnt/external-media/
sudo chown -R $USER:$USER /mnt/backups/
```

## Docker compose file

```yaml
services:
    samba:
        image: dperson/samba
        container_name: samba
        restart: unless-stopped
        cpu_shares: 128
        blkio_config:
            weight: 100
        ports:
            - '139:139'
            - '445:445'
        volumes:
            - /mnt/backups:/mnt/backups
            - /mnt/external-media:/mnt/media
        environment:
            - USER=admin;${SAMBA_PASSWORD}
        command: >
            -s "BackupsHomeAssistant;/mnt/backups;yes;no;no;admin"
            -s "Media;/mnt/media;yes;no;no;admin"
            -p

    jellyfin:
        image: jellyfin/jellyfin
        container_name: jellyfin
        restart: unless-stopped
        network_mode: host
        cpu_shares: 1024
        blkio_config:
            weight: 1000
        volumes:
            - ./jellyfin-config:/config
            - /mnt/external-media:/media
            - type: tmpfs
              target: /transcode
              tmpfs:
                  size: 1000000000
        devices:
            - /dev/dri:/dev/dri

    glances:
        image: nicolargo/glances:latest-full
        container_name: glances
        restart: unless-stopped
        network_mode: host
        pid: host
        volumes:
            - /var/run/docker.sock:/var/run/docker.sock:ro
        environment:
            - 'GLANCES_OPT=-w'
            - TZ=Europe/Paris
```

# Backup an SD card

Shutdown the pi and put the SD card into a reader on another computer

## Check SD card disk name

```bash
diskutil list # Replace with rdiskX below and keep 'r' in front of the disk name
```

## Backup SD card

```bash
sudo dd if=/dev/rdisk4 of=backup_mercure_20260426.img bs=4M status=progress
```

## Shrink image

```bash
docker run --privileged=true --rm --volume $(pwd):/tmp fvillart/pishrink pishrink.sh -zv backup_mercure_20260426.img backup_mercure_20260426_shrinked.img
```

## To write image, use Raspberry Pi Imager

Choose "Use a custom image" and select the backup_mercure_20260426_shrinked.img.gz file
