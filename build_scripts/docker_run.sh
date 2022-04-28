#!/bin/bash
set -e -u -x

output="$1"

function repair_wheel {
    wheel="$1"
    if ! auditwheel show "$wheel"; then
        echo "Skipping non-platform wheel $wheel"
    else
        auditwheel repair "$wheel" --plat "$AUDITWHEEL_PLAT" -w "$output"
    fi
}



OLDPATH=${PATH}
for BNAME in "${@:2}"
do
    export PATH="/opt/python/$BNAME/bin:$OLDPATH"
    pip wheel . --no-deps -w dist/
    pip install dist/craytraverse-*-"$BNAME"-linux_x86_64.whl
    py.test
    FILE=tests/failures
    if [ -f "$FILE" ]; then
        cp tests/failures "$1"/"$BNAME"_linux_failures.txt
    fi
    repair_wheel dist/craytraverse-*-"$BNAME"-*.whl
    
done








