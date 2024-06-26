#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for craytraverse.crenderer.crcontrib"""
import os
import shutil

from craytraverse.renderer import Rcontrib
import numpy as np
import pytest


@pytest.fixture(scope="module")
def tmpdir(tmp_path_factory):
    data = str(tmp_path_factory.mktemp("data"))
    shutil.copytree('tests/craytraverse/', data + '/test')
    cpath = os.getcwd()
    # use temp
    path = data + '/test'
    # uncomment to use actual (to debug results)
    # path = cpath + '/tests/craytraverse'
    os.chdir(path)
    yield path
    os.chdir(cpath)


@pytest.fixture(scope="function")
def tmpdir2(tmp_path_factory):
    data = str(tmp_path_factory.mktemp("data"))
    shutil.copytree('tests/rcontrib_reset/', data + '/test2')
    cpath = os.getcwd()
    # use temp
    path = data + '/test2'
    # uncomment to use actual (to debug results)
    path = cpath + '/tests/rcontrib_reset'
    os.chdir(path)
    yield path
    os.chdir(cpath)


def test_rcontrib_reset(tmpdir2):
    args = "-V+ -I+ -ab 3 -ad 60000 -lw 1e-5"
    r = Rcontrib(args, "box.oct", skyres=6, ground=False, modname="skyMat")
    vec = np.array(((0,0,1,0,0,1),), dtype=float)
    r1 = r(vec)
    r.reset()
    r = Rcontrib(args, "box.oct", skyres=6, ground=False, modname="skyMat")
    r2 = r(vec)
    r.reset()
    assert np.allclose(r1, r2, atol=.05)


# breaks test/example foor soome reason (must be in c-code!!!)
def test_rcontrib_call(capfd, tmpdir):
    check = """0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
    0	0	0	0	0	3.856109e-02	3.814993e-02	3.793787e-02
    3.327852e-02	3.296014e-02	3.279520e-02	2.923070e-02
    2.896514e-02	2.880886e-02	3.528423e-02	3.509728e-02
    3.491599e-02	0	0	0	0	0	0	2.865155e-02	2.836000e-02
    2.821047e-02	1.509501e-02	1.504926e-02	1.502639e-02
    1.658427e-02	1.656674e-02	1.654001e-02	2.553548e-02
    2.553853e-02	2.545625e-02	0	0	0	0	0	0
    2.978601e-02	2.948140e-02	2.932152e-02	1.673053e-02
    1.670661e-02	1.669451e-02	1.618107e-02	1.618137e-02
    1.617045e-02	2.250982e-02	2.252463e-02	2.248511e-02	0	0
    0	0	0	0	3.336588e-02	3.316102e-02	3.305506e-02
    2.429552e-02	2.425999e-02	2.424214e-02	2.262842e-02
    2.260985e-02	2.257240e-02	2.868575e-02	2.868504e-02
    2.860816e-02	0	0	0	0	0	0	0	0	0	0	0	0	0
    0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
    0	0	0	0	0	0	0	0	0	0	0	3.722431e-02	3.687026e-02
    3.669002e-02	2.877378e-02	2.855665e-02	2.844648e-02
    2.576764e-02	2.560148e-02	2.549271e-02	2.994366e-02
    2.982973e-02	2.971956e-02	0	0	0	0	0	0	2.890151e-02
    2.860205e-02	2.845215e-02	1.642967e-02	1.639420e-02
    1.637495e-02	1.500287e-02	1.499461e-02	1.497691e-02
    2.550464e-02	2.553317e-02	2.543306e-02	0	0	0	0	0	0
    3.017941e-02	2.988612e-02	2.973922e-02	1.541000e-02
    1.538210e-02	1.536661e-02	1.482810e-02	1.483092e-02
    1.481656e-02	2.322479e-02	2.324641e-02	2.318987e-02	0	0
    0	0	0	0	3.275824e-02	3.259909e-02	3.251714e-02
    2.281902e-02	2.278321e-02	2.276147e-02	2.377092e-02
    2.374596e-02	2.370305e-02	2.831376e-02	2.831454e-02
    2.820505e-02	0	0	0	0	0	0	0	0	0	0	0	0	0
    0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
    0	0	0	0	0	0	0	0	0	0	0	3.499534e-02
    3.471379e-02	3.456980e-02	2.739477e-02	2.717554e-02
    2.706338e-02	2.455669e-02	2.439277e-02	2.429379e-02
    3.128208e-02	3.118257e-02	3.107150e-02	0	0	0	0	0	0
    2.643443e-02	2.624432e-02	2.614772e-02	1.611248e-02
    1.608939e-02	1.607626e-02	1.633184e-02	1.632764e-02
    1.631082e-02	2.502951e-02	2.504394e-02	2.497859e-02
    0	0	0	0	0	0	2.850137e-02	2.831181e-02	2.821563e-02
    1.615438e-02	1.613810e-02	1.612845e-02	1.546534e-02
    1.546205e-02	1.545176e-02	2.057833e-02	2.059490e-02
    2.054027e-02	0	0	0	0	0	0	3.132820e-02	3.120117e-02
    3.113406e-02	2.217779e-02	2.212565e-02	2.209958e-02
    2.350735e-02	2.344759e-02	2.340008e-02	2.975164e-02
    2.969625e-02	2.961243e-02	0	0	0	0	0	0	0	0	0
    0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
    0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
    3.545513e-02	3.509608e-02	3.491402e-02	3.144867e-02
    3.112990e-02	3.096678e-02	2.881183e-02	2.855065e-02
    2.840313e-02	3.283797e-02	3.266260e-02	3.251936e-02	0	0
    0	0	0	0	2.835480e-02	2.816243e-02	2.806360e-02
    1.553581e-02	1.550139e-02	1.547819e-02	1.594568e-02
    1.592585e-02	1.590788e-02	2.626723e-02	2.625518e-02
    2.621342e-02	0	0	0	0	0	0	2.903953e-02	2.884058e-02
    2.874110e-02	1.505572e-02	1.503763e-02	1.502849e-02
    1.467683e-02	1.467532e-02	1.466603e-02	2.263451e-02
    2.264837e-02	2.260736e-02	0	0	0	0	0	0	3.114938e-02
    3.100993e-02	3.093875e-02	2.269041e-02	2.264525e-02
    2.262267e-02	2.485945e-02	2.481083e-02	2.476464e-02
    2.930650e-02	2.927448e-02	2.919439e-02	0	0	0	0	0
    0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
    0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
    0	0	3.545513e-02	3.509608e-02	3.491402e-02	3.144867e-02
    3.112990e-02	3.096678e-02	2.881183e-02	2.855065e-02
    2.840313e-02	3.283797e-02	3.266260e-02	3.251936e-02	0	0
    0	0	0	0	2.835480e-02	2.816243e-02	2.806360e-02
    1.553581e-02	1.550139e-02	1.547819e-02	1.594568e-02
    1.592585e-02	1.590788e-02	2.626723e-02	2.625518e-02
    2.621342e-02	0	0	0	0	0	0	2.903953e-02	2.884058e-02
    2.874110e-02	1.505572e-02	1.503763e-02	1.502849e-02
    1.467683e-02	1.467532e-02	1.466603e-02	2.263451e-02
    2.264837e-02	2.260736e-02	0	0	0	0	0	0
    3.114938e-02	3.100993e-02	3.093875e-02	2.269041e-02
    2.264525e-02	2.262267e-02	2.485945e-02	2.481083e-02
    2.476464e-02	2.930650e-02	2.927448e-02	2.919439e-02
    0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
    0	0	0"""
    check = np.fromstring(check, sep=' ').reshape(-1, 36, 3)
    checkb = np.einsum('ikj,j->ik', check, [47.435/179, 119.93/179, 11.635/179]).reshape(-1, 36, 1)

    args = "-V+ -I+ -ab 2 -ad 600 -as 300 -lw 1e-5"
    engine = Rcontrib(args, "sky2.oct", skyres=6, ground=False)

    vecs = np.loadtxt('rays2.txt')
    test = engine(vecs)
    engine.reset()
    assert np.allclose(checkb, test, atol=.05)

    engine = Rcontrib(args + ' -Z-', "sky2.oct", skyres=6, ground=False)

    vecs = np.loadtxt('rays2.txt')
    test = engine(vecs)
    assert np.allclose(check, test, atol=.05)
    engine.reset()
    
    



