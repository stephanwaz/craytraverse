#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for raytraverse.craytraverse"""
import os
import shutil
import sys
import re

from craytraverse.renderer import Rtrace
import numpy as np
import pytest




gargs = ['rtrace', '-n', '12', '-u+', '-ab', '16', '-av', '0', '0', '0', 
         '-aa', '0', '-as', '0', '-dc', '1', '-dt', '0', '-lr', '-14', 
         '-ad', '1000', '-lw', '0.00004', '-st', '0', '-ss', '16', '-w-']


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


def test_empty_reset(tmpdir):
    r = Rtrace(" ".join(gargs[1:]), "sky.oct")
    r.reset()
    r.reset()
    assert True


def test_rtrace_call(tmpdir):
    args = ['rtrace', '-ab', '1', '-ar', '600', '-ad', '2000', '-aa', '.2', '-as', '1500', '-I+']
    check = """4.244131e-01    4.244131e-01    4.244131e-01
4.289989e-01    4.289989e-01    4.289989e-01
4.289069e-01    4.289069e-01    4.289069e-01
4.386518e-01    4.386518e-01    4.386518e-01
6.283185e+00    6.283185e+00    6.283185e+00"""
    check = np.fromstring(check, sep=' ').reshape(-1, 3)
    check2 = np.einsum('ij,j->i', check, [47.435/179, 119.93/179, 11.635/179])
    # first load
    r = Rtrace(" ".join(args[1:]), "sky.oct", 12)

    vecs = np.loadtxt('rays.txt')
    ans = r(vecs)
    assert np.allclose(check, ans, atol=.03)

    # change output
    r.update_ospec('ZL')
    ans = r(vecs)
    assert np.allclose(check2, ans[:, 0], atol=.03)
    # #
    # # reload and change output to float
    r.reset()
    args2 = args + ['-oZ']

    r = Rtrace(" ".join(args2[1:]), "sky.oct", 12)
    #
    test3 = r(vecs).ravel()
    assert np.allclose(check2, test3, atol=.03)
    # #
    # reload new scene
    r.load_scene("sky.oct")
    test3 = r(vecs).ravel()
    assert np.allclose(check2, test3, atol=.03)
    # #
    # # # change args
    args3 = '-lr 1 -oZ -I'

    r.set_args(args3, 12)

    test3 = r(vecs).ravel()
    assert np.allclose([0, 0, 0, 0, np.pi*2], test3, atol=.03)
#     # #
    # # change back
    r.set_args(" ".join(args2[1:]), 12)

    test3 = r(vecs).ravel()
    assert np.allclose(check2, test3, atol=.03)

    # load sources
    r = Rtrace("-lr 1 -oZ", "scene.oct", 1)
    r.load_source("sun.rad")
    test = r(vecs).ravel()
    r.load_source("sun2.rad")
    test2 = r(vecs).ravel()
    assert np.allclose(test * 2, test2, atol=.03)
    check2 = [3.930521e-03, 3.930521e-03, 3.930521e-03, 3.930521e-03, 1.000000e+01]
    assert np.allclose(test, check2, atol=.03)
    # #
    # #
    r.set_args(" ".join(args[1:]))
    test2 = r(vecs).ravel()
    r.load_source("sky.rad")
    test3 = r(vecs).ravel()
    r.load_source("sun2.rad", 0)
    test4 = r(vecs).ravel()
    r.load_source("sun.rad")
    test5 = r(vecs).ravel()
    assert np.allclose(test2 + test3, test4, atol=.03)
    assert np.allclose(test2, test5, atol=.03)
    r.reset()


def test_ambient_reset(tmpdir):

    args = "-u- -ab 1 -ar 1000 -ad 4000 -aa .05 -as 2000 -I+"

    r = Rtrace(args, "scene.oct")

    vecs = np.loadtxt('rays2.txt')

    def load_sun(sun, val, af=None):
        srcdef = f'tmp_sun.rad'
        f = open(srcdef, 'w')
        sdef = (f"void light solar 0 0 3 {val} {val} {val}\n"
                f"solar source sun 0 0 4 {sun[0]} {sun[1]} {sun[2]} 0.5333\n")
        f.write(sdef)
        f.close()
        if af is not None:
            r.set_args(args + f' -af {af}')
        r.load_source(srcdef, ambfile=af)
        os.remove(srcdef)

    load_sun((0, -.5, 1), 1000000, "temp.amb")
    r(vecs)
    a1 = r(vecs).ravel()
    load_sun((0, -.5, 1), 1000000, "temp2.amb")
    r(vecs)
    a2 = r(vecs).ravel()

    load_sun((-.5, -.5, 1), 2000000, "temp3.amb")
    r(vecs)
    a3 = r(vecs).ravel()

    load_sun((0, -.5, 1), 1000000, "temp.amb")
    a1a = r(vecs).ravel()
    load_sun((0, -.5, 1), 1000000, "temp2.amb")
    a2a = r(vecs).ravel()
    load_sun((0, -.5, 1), 1000000, "temp4.amb")
    r(vecs)
    a4 = r(vecs).ravel()

    r.set_args(" ".join(gargs[1:]) + " -I+ -ab 1 -c 30")
    aa0 = r(vecs).ravel()

    r.set_args(args)
    load_sun((-.5, -.5, 1), 2000000, "temp3.amb")
    a3a = r(vecs).ravel()
    assert(np.allclose(a1, a1a))
    assert (np.allclose(a2, a2a))
    assert (np.allclose(a3, a3a))
    assert 1e-8 < np.sum(np.abs(a2 - a4)) < .5
    load_sun((-.5, -.5, 1), 2000000, "temp5.amb")
    noamb = r(vecs).ravel()
    assert 1e-8 < np.sum(np.abs(noamb - a3)) < 1
    r.reset()
# #
# #
def test_ambient_nostore(tmpdir):

    args = "-u- -ab 1 -ar 1000 -ad 4000 -aa .05 -as 2000 -I+"

    r = Rtrace(args, "scene.oct")

    vecs = np.loadtxt('rays2.txt')

    def load_sun(sun, val):
        srcdef = f'tmp_sun.rad'
        f = open(srcdef, 'w')
        sdef = (f"void light solar 0 0 3 {val} {val} {val}\n"
                f"solar source sun 0 0 4 {sun[0]} {sun[1]} {sun[2]} 0.5333\n")
        f.write(sdef)
        f.close()
        r.load_source(srcdef)
        os.remove(srcdef)

    load_sun((0, -.5, 1), 1000000)

    # ambient values are not shared
    r(vecs)
    an2 = r(vecs).ravel()
    an3 = r(vecs).ravel()
    assert 1e-8 < np.sum(np.abs(an2 - an3)) < .5

    # ambient values are shared (vectors repeated, 1 process)
    an4 = r(np.repeat(vecs, 2, 0)).reshape(-1, 2).T
    assert (np.allclose(an4[0], an4[1]))
    r.reset()


def test_get_sources(tmpdir):

    args = "-u- -ab 1 -ad 4000 -aa 0 -as 2000 -I+"

    r = Rtrace(args, "mirror.oct")

    def load_sun(sun, val):
        srcdef = f'tmp_sun.rad'
        f = open(srcdef, 'w')
        sdef = (f"void light solar 0 0 3 {val} {val} {val}\n"
                f"solar source sun 0 0 4 {sun[0]} {sun[1]} {sun[2]} 0.5333\n")
        f.write(sdef)
        f.close()
        r.load_source(srcdef)
        os.remove(srcdef)

    load_sun((0, -.5, 1), 1000000)
    r.load_source("light.rad", 0)
    sources, distant = r.instance.get_sources()
    a = [0., -0.4472136, 0.89442719]
    assert np.allclose(a, sources[0, 0:3])


def test_get_model_details(tmpdir):
    rays = """4.00000e+00 4.00000e+00 1.25000e+00 -6.92105e-01 -2.04895e-01 6.92105e-01
4.00000e+00 4.00000e+00 1.25000e+00 -4.41078e-01 1.65074e-01 8.82157e-01
4.00000e+00 4.00000e+00 1.25000e+00 0.00000e+00 3.09017e-01 9.51057e-01
4.00000e+00 4.00000e+00 1.25000e+00 4.41078e-01 1.65074e-01 8.82157e-01
4.00000e+00 4.00000e+00 1.25000e+00 6.92105e-01 -2.04895e-01 6.92105e-01
4.00000e+00 4.00000e+00 1.25000e+00 -8.82157e-01 1.65074e-01 4.41078e-01
4.00000e+00 4.00000e+00 1.25000e+00 -5.48839e-01 6.30517e-01 5.48839e-01
4.00000e+00 4.00000e+00 1.25000e+00 0.00000e+00 8.09017e-01 5.87785e-01
4.00000e+00 4.00000e+00 1.25000e+00 5.48839e-01 6.30517e-01 5.48839e-01
4.00000e+00 4.00000e+00 1.25000e+00 8.82157e-01 1.65074e-01 4.41078e-01
4.00000e+00 4.00000e+00 1.25000e+00 -9.51057e-01 3.09017e-01 0.00000e+00
4.00000e+00 4.00000e+00 1.25000e+00 -5.87785e-01 8.09017e-01 0.00000e+00
4.00000e+00 4.00000e+00 1.25000e+00 0.00000e+00 1.00000e+00 0.00000e+00
4.00000e+00 4.00000e+00 1.25000e+00 5.87785e-01 8.09017e-01 0.00000e+00
4.00000e+00 4.00000e+00 1.25000e+00 9.51057e-01 3.09017e-01 0.00000e+00
4.00000e+00 4.00000e+00 1.25000e+00 -8.82157e-01 1.65074e-01 -4.41078e-01
4.00000e+00 4.00000e+00 1.25000e+00 -5.48839e-01 6.30517e-01 -5.48839e-01
4.00000e+00 4.00000e+00 1.25000e+00 0.00000e+00 8.09017e-01 -5.87785e-01
4.00000e+00 4.00000e+00 1.25000e+00 5.48839e-01 6.30517e-01 -5.48839e-01
4.00000e+00 4.00000e+00 1.25000e+00 8.82157e-01 1.65074e-01 -4.41078e-01
4.00000e+00 4.00000e+00 1.25000e+00 -6.92105e-01 -2.04895e-01 -6.92105e-01
4.00000e+00 4.00000e+00 1.25000e+00 -4.41078e-01 1.65074e-01 -8.82157e-01
4.00000e+00 4.00000e+00 1.25000e+00 0.00000e+00 3.09017e-01 -9.51057e-01
4.00000e+00 4.00000e+00 1.25000e+00 4.41078e-01 1.65074e-01 -8.82157e-01
4.00000e+00 4.00000e+00 1.25000e+00 6.92105e-01 -2.04895e-01 -6.92105e-01"""
    rays = np.fromstring(rays, sep=' ').reshape(-1, 6)
    check = """0.000000e+00    0.000000e+00    0.000000e+00    3.973387e+00    0.000000e+00    0.000000e+00    1.000000e+00    CLNG
0.000000e+00    0.000000e+00    0.000000e+00    3.117359e+00    0.000000e+00    0.000000e+00    1.000000e+00    CLNG
1.028329e+00    1.028329e+00    1.028329e+00    3.242005e+00    0.000000e+00    0.000000e+00    -1.000000e+00    sglz
1.027430e+00    1.027430e+00    1.027430e+00    3.495217e+00    0.000000e+00    0.000000e+00    -1.000000e+00    sglz
0.000000e+00    0.000000e+00    0.000000e+00    3.973387e+00    0.000000e+00    0.000000e+00    1.000000e+00    CLNG
0.000000e+00    0.000000e+00    0.000000e+00    4.534341e+00    -1.000000e+00    0.000000e+00    0.000000e+00    EXT_WALL
0.000000e+00    0.000000e+00    0.000000e+00    5.010577e+00    0.000000e+00    0.000000e+00    1.000000e+00    CLNG
0.000000e+00    0.000000e+00    0.000000e+00    4.678581e+00    0.000000e+00    0.000000e+00    1.000000e+00    CLNG
0.000000e+00    0.000000e+00    0.000000e+00    5.010577e+00    0.000000e+00    0.000000e+00    1.000000e+00    CLNG
0.000000e+00    0.000000e+00    0.000000e+00    6.234726e+00    0.000000e+00    0.000000e+00    1.000000e+00    CLNG
0.000000e+00    0.000000e+00    0.000000e+00    4.205849e+00    -1.000000e+00    0.000000e+00    0.000000e+00    EXT_WALL
0.000000e+00    0.000000e+00    0.000000e+00    6.805208e+00    -1.000000e+00    0.000000e+00    0.000000e+00    EXT_WALL
0.000000e+00    0.000000e+00    0.000000e+00    1.600000e+01    0.000000e+00    -1.000000e+00    0.000000e+00    EXT_WALL
5.728542e-01    5.728542e-01    5.728542e-01    1.085601e+01    -1.000000e+00    0.000000e+00    0.000000e+00    glz
0.000000e+00    0.000000e+00    0.000000e+00    6.308773e+00    1.000000e+00    0.000000e+00    0.000000e+00    EXT_WALL
0.000000e+00    0.000000e+00    0.000000e+00    2.833966e+00    0.000000e+00    0.000000e+00    1.000000e+00    FLOR
0.000000e+00    0.000000e+00    0.000000e+00    2.277535e+00    0.000000e+00    0.000000e+00    1.000000e+00    FLOR
0.000000e+00    0.000000e+00    0.000000e+00    2.126628e+00    0.000000e+00    0.000000e+00    1.000000e+00    FLOR
0.000000e+00    0.000000e+00    0.000000e+00    2.277535e+00    0.000000e+00    0.000000e+00    1.000000e+00    FLOR
0.000000e+00    0.000000e+00    0.000000e+00    2.833966e+00    0.000000e+00    0.000000e+00    1.000000e+00    FLOR
0.000000e+00    0.000000e+00    0.000000e+00    1.806085e+00    0.000000e+00    0.000000e+00    1.000000e+00    FLOR
0.000000e+00    0.000000e+00    0.000000e+00    1.416981e+00    0.000000e+00    0.000000e+00    1.000000e+00    FLOR
0.000000e+00    0.000000e+00    0.000000e+00    1.314328e+00    0.000000e+00    0.000000e+00    1.000000e+00    FLOR
0.000000e+00    0.000000e+00    0.000000e+00    1.416981e+00    0.000000e+00    0.000000e+00    1.000000e+00    FLOR
0.000000e+00    0.000000e+00    0.000000e+00    1.806085e+00    0.000000e+00    0.000000e+00    1.000000e+00    FLOR"""
    check_d = np.asarray([[float(i) for i in j.split()[:-1]] for j in check.splitlines()])
    check_m = [j.split()[-1] for j in check.splitlines()]

    Rtrace().reset()
    r = Rtrace("-u- -ab 0", "sky.oct")

    r.update_ospec("vLNM")
    test = r(rays)
    mtest = test[:,-1]
    assert np.allclose(check_d, test[:,:-1])
    for c in set(check_m):
        m = mtest[[i == c for i in check_m]]
        assert np.all(m == m[0])
#
