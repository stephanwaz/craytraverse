#!/bin/bash

# this starts a container inside dev environment for live edits/testing from mac side.

# Open Docker, only if is not running
if (! docker stats --no-stream &> /dev/null); then
  # On Mac OS this would be the terminal command to launch Docker
  open /Applications/Docker.app
# Wait until Docker daemon is running and has completed initialisation
while (! docker stats --no-stream &> /dev/null); do
  # Docker takes a few seconds to initialize
  echo "Waiting for Docker to launch..."
  sleep 10
done
fi

#pip wheel . --no-deps -w dist/
#pip install dist/craytraverse-0.1.6-cp310-cp310-linux_x86_64.whl
docker run -it --platform=linux/amd64 --name crayte --workdir="/working" --mount type=bind,source="$(pwd)",target=/working craytmany /bin/bash -c 'export PATH=/opt/python/cp310-cp310/bin:$PATH; /bin/bash'
docker rm crayte