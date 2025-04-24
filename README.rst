====================
craytraverse (0.1.7)
====================

.. image:: https://img.shields.io/pypi/v/craytraverse?style=flat-square
    :target: https://pypi.org/project/craytraverse
    :alt: PyPI

.. image:: https://img.shields.io/pypi/l/craytraverse?style=flat-square
    :target: https://www.mozilla.org/en-US/MPL/2.0/
    :alt: PyPI - License

c/c++ libraries for raytraverse, including radiance based render classes.

* Free software: Mozilla Public License 2.0 (MPL 2.0)
* Documentation: https://raytraverse.readthedocs.io/en/latest/.


Installation
------------
The easiest way to install craytraverse is with pip::

    pip install --upgrade pip setuptools wheel
    pip install craytraverse

or if you have cloned this repository::

    cd path/to/this/file
    git submodule init
    git submodule update
    make update


Build
-----

Install Docker: https://www.docker.com/products/docker-desktop/
within build_scripts::

    docker build --tag craytmany .

run scripts in build_scripts from ./, for example::

    ./build_scripts/dist_check.sh

will, after cleaning and testing, (with prompts at each step):

    1. build craytraverse locally
    2. launch a docker container and build/test with python3.10 in a manylinux enivronment

for live testing inside linux environment::

    ./build_scripts/edit_linux.sh

after it starts::

    pip wheel . --no-deps -w dist/
    pip install dist/craytraverse-*.*.*-cp310-cp310-linux_x86_64.whl

use build_scripts/release.sh to build all versions, which calls dist_versions.sh.

docker_run.sh is used on the linux side, build_wheel will test build a wheel for
a single version specified on the command line.
