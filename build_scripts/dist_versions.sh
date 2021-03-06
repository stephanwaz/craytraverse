make clean
python setup.py sdist
source ~/venv/dev310/bin/activate
pip wheel . --no-deps -w dist/
source ~/venv/dev39/bin/activate
pip wheel . --no-deps -w dist/
source ~/venv/dev38/bin/activate
pip wheel . --no-deps -w dist/
source ~/venv/dev/bin/activate
pip wheel . --no-deps -w dist/

docker build . --tag crayttest
docker run -it --name crayt0 --mount type=bind,source="$(pwd)"/dist,target=/wheelhouse crayttest
docker rm crayt0
docker image rm crayttest
# to interactive:
# docker run -it --name rayt0 --mount type=bind,source="$(pwd)",target=/hostsrc rayttest /bin/bash
# # docker image rm rayttest


 

 ls -l dist
