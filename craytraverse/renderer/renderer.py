# -*- coding: utf-8 -*-
# Copyright (c) 2020 Stephen Wasilewski, HSLU and EPFL
# =======================================================================
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# =======================================================================
import shlex


class Renderer:
    """Virtual class for wrapping c++ Radiance renderer executable classes

    Do not use directly, either subclass or use existing: Rtrace, Rcontrib
    """

    name = "radiance_virtual"
    instance = None
    srcn = 1
    features = 1
    args = None
    _args = None
    nproc = 1

    def __init__(self, rayargs=None, scene=None, nproc=1):
        if rayargs is not None and scene is not None:
            self.set_args(rayargs, nproc)
            self.load_scene(scene)

    @classmethod
    def __call__(cls, rays):
        return cls.instance(rays)

    def __getstate__(self):
        state = type(self).__dict__.copy()
        cms = []
        state.pop("instance")
        for k in state.keys():
            if type(state[k]) == classmethod or k[0:2] == "__":
                cms.append(k)
        [state.pop(i) for i in cms]
        return state

    def __setstate__(self, state):
        for k in state.keys():
            setattr(type(self), k, state[k])

    def run(self, *args, **kwargs):
        """alias for call, for consistency with SamplerPt classes for nested
        dimensions of evaluation"""
        return self(args[0])

    @classmethod
    def reset(cls):
        """reset engine instance and unset associated attributees"""
        cls.instance.reset()
        cls.scene = None
        cls.args = None
        cls._args = None

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
        cls.nproc = nproc
        cls.args = args
        cls._args = shlex.split(f"{cls.name} -n {nproc} {args}")
        nproc = cls.instance.initialize(cls._args)
        if nproc < 0:
            raise ValueError(f"Could not initialize {cls.__name__} with "
                             f"arguments: '{' '.join(cls._args)}'")

    @classmethod
    def load_scene(cls, scene):
        """load octree file to engine instance

        Parameters
        ----------
        scene: str
            path to octree file

        Raises
        ------
        ValueError:
            can only be called after set_args, otherwise engine instance
            will abort.
        """
        if cls._args is None:
            raise ValueError(f'{cls.__name__} instance args must be '
                             'initialized before scene is loaded')
        cls.scene = scene
        cls.instance.load_scene(scene)
