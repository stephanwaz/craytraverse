# -*- coding: utf-8 -*-
# Copyright (c) 2020 Stephen Wasilewski, HSLU and EPFL
# =======================================================================
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# =======================================================================
import re

from craytraverse.renderer.renderer import Renderer
from craytraverse.crenderer import cRcontrib

rcontrib_instance = cRcontrib.get_instance()


class Rcontrib(Renderer):
    """singleton wrapper for c++ raytrraverse.crenderer.cRcontrib class

    this class sets default arguments, helps with initialization and setting
    cpu limits of the cRcontrib instance. see raytrraverse.crenderer.cRcontrib
    for more details.

    Parameters
    ----------
    rayargs: str, optional
        argument string (options and flags only) raises ValueError if arguments
        are not recognized by cRtrace.
    scene: str, optional
        path to octree
    nproc: int, optional
    skyres: int, optional
        resolution of sky patches (sqrt(patches / hemisphere)).
        So if skyres=18, each patch
        will be 100 sq. degrees (0.03046174197 steradians) and there will be
        18 * 18 = 324 sky patches.
    modname: str, optional
        passed the -m option of cRcontrib initialization
    ground: bool, optional
        if True include a ground source (included as a final bin)


    Examples
    --------

    Basic Initialization and call::

        r = renderer.Rcontrib(args, scene)
        ans = r(vecs)
        # ans.shape -> (vecs.shape[0], 325)
    """
    name = 'rcontrib'
    instance = rcontrib_instance
    ground = True
    skyres = 15
    srcn = 226
    modname = "skyglow"

    def __init__(self, rayargs=None, scene=None, nproc=1,
                 skyres=15, modname='skyglow', ground=True):
        scene = self.setup(scene, ground, modname, skyres)
        super().__init__(rayargs, scene, nproc=nproc)

    def __setstate__(self, state):
        super().__setstate__(state)
        type(self).instance = rcontrib_instance

    @classmethod
    def setup(cls, scene=None, ground=True, modname="skyglow", skyres=15):
        """set class attributes for proper argument initialization

        Parameters
        ----------
        scene: str, optional
            path to octree
        ground: bool, optional
            if True include a ground source (included as a final bin)
        modname: str, optional
            passed the -m option of cRcontrib initialization
        skyres: float, optional
            resolution of sky patches (sqrt(patches / hemisphere)).
            So if skyres=10, each patch will be 100 sq. degrees
            (0.03046174197 steradians) and there will be 18 * 18 = 324 sky
            patches.

        Returns
        -------
        scene: str
            path to scene with added sky definition

        """
        cls.ground = ground
        cls.skyres = skyres
        cls.srcn = cls.skyres**2 + ground
        cls.modname = modname
        return scene

    @classmethod
    def set_args(cls, args, nproc=1):
        """prepare arguments to call engine instance initialization

        Parameters
        ----------
        args: str
            rendering options
        nproc: int, optional
            cpu limit

        """
        args = (f" -V+ {args} -w- -e 'side:{cls.skyres}' -f scbins.cal "
                f"-b bin -bn {cls.srcn} -m {cls.modname}")
        bright = True
        for z in re.findall(r"-Z.?", args):
            if z[-1] in "Z ":
                bright = not bright
            elif z[-1] in "+yYtT1":
                bright = True
            else:
                bright = False
        if bright:
            cls.features = 1
        else:
            cls.features = 3
        super().set_args(args, nproc)
