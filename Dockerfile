# syntax=docker/dockerfile:1

FROM  --platform=linux/amd64 craytmany

SHELL ["/bin/bash", "-c"]

WORKDIR /app
ADD ./dist/craytraverse-0.1.7.tar.gz ./
WORKDIR /app/craytraverse-0.1.7

CMD /bin/bash build_scripts/docker_run.sh /wheelhouse/ cp37-cp37m cp38-cp38 cp39-cp39 cp310-cp310