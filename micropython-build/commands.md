# Build the Micropython firmware
This section explains how to run a container for building the Micropython firmware and adding a few custom python modules into it.

The project uses a container prepared by Jan Pobořil: https://gitlab.com/janpoboril/micropython-docker-build


## Micropython version
Check the Dockerfile for the version of Micropython that will be checked out into the container (e.g. ARG VERSION=v1.17).

## Build the firmware
 The following steps are done each time a new build is required and usually triggerred trough VS Code (check last section of this file on "VS Code integration")
```
docker build -t micropython -f Dockerfile .
```
The previous command creates an image and also copy files from the folder "modules" into the container:

> from path-to-local-folder/modules/* to container/micropython/ports/esp8266/modules/
### Run container
```
docker run -d --name=micropython micropython bash
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

```
docker rm -f micropython && docker system prune -f
```
## VS Code integration

Check the _/.vscode/tasks.json_ file for building the firmware.
Launch the "Build custom micropython" command in VS Code by pressing CMD + SHIFT + B.


