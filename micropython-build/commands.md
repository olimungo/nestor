# Build the Micropython firmware
This section explains how to run a container for building the Micropython firmware and adding a few custom python modules into it.

## Micropython version
Check the file Dockerfile.sources for the version of Micropython that will be downloaded into the container (ARG VERSION=x.y).
## Create images for building the Micropython firmware
The following steps are only executed once
> One line command !!!
```
docker build -t micropython-base -f Dockerfile.base . && \
docker build -t micropython-sources -f Dockerfile.sources . && \
docker build -t micropython-build -f Dockerfile.build . &&
docker rmi micropython-base micropython-sources && \
docker system prune -f
```
## Build the firmware
 The following steps are done each time a new build is required and usually triggerred trough VS Code (check last section of this file on "VS Code integration")
```
docker build -t micropython -f Dockerfile .
```
The previous command creates an image and also copy files from the folder "modules" into the container:

> from path-to-local-folder/modules/* to container/micropython/ports/esp8266/modules/
### Run container
```
docker run -d --name=micropython micropython
```
### Enter the previously created container

This step is only required when there's a need to check files inside the container.
Other than that, just skip this step.
```
docker exec -it micropython /bin/bash -l
```
### Retrieve firmware
```
docker cp micropython:/micropython/ports/esp8266/build-GENERIC/firmware-combined.bin ..
```
### Clean
> One line command !!!
```
docker rm -f micropython && \
docker rmi -f micropython && \
docker system prune -f
```
## VS Code integration

Check the /.vscode/tasks.json file for commands for VS Code (CTRL for Windows or CMD for Mac + SHIFT + B)


