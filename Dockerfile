# syntax=docker/dockerfile:1

FROM craytmany:latest

SHELL ["/bin/bash", "-c"]

WORKDIR /app
ADD ./dist/craytraverse-0.1.1.tar.gz ./
WORKDIR /app/craytraverse-0.1.1

CMD /bin/bash build_scripts/docker_run.sh cp37-cp37m cp38-cp38 cp39-cp39 cp310-cp310