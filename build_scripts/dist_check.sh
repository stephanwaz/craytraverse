make clean
py.test

echo -n "proceed to test build (y/n)? "
read -r answer

if [ "$answer" != "${answer#[Yy]}" ] ;then

    python setup.py sdist
    pip wheel . --no-deps -w dist/

    echo -n "proceed to docker build/test (y/n)? "
    read -r answer

    if [ "$answer" != "${answer#[Yy]}" ] ;then

        docker build . --tag crayttest
        docker run -it --name crayt0 --mount type=bind,source="$(pwd)"/dist,target=/wheelhouse crayttest /bin/bash build_scripts/docker_run.sh /wheelhouse/ cp39-cp39
        docker rm crayt0
        docker image rm crayttest
    fi

    ls -l dist

    echo check files and git commit ...

 fi
