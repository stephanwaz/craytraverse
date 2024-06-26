#!/bin/bash


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

docker run -it --platform=linux/amd64 --name crayte --workdir="/working" --mount type=bind,source="$(pwd)",target=/working craytmany /bin/bash -c "build_scripts/docker_run.sh dist/ cp$1-cp$1"
docker rm crayte