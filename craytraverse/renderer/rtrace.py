# -*- coding: utf-8 -*-
# Copyright (c) 2020 Stephen Wasilewski, HSLU and EPFL
# =======================================================================
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# =======================================================================
import re
import sys

from craytraverse.renderer.renderer import Renderer
from craytraverse.crenderer import cRtrace

rtrace_instance = cRtrace.get_instance()


class Rtrace(Renderer):
    """singleton wrapper for c++ raytrraverse.crenderer.cRtrace class

    this class sets default arguments, helps with initialization and setting
    cpu limits of the cRtrace instance. see raytraverse.crenderer.cRtrace
    for more details.

    Parameters
    ----------
    rayargs: str, optional
        argument string (options and flags only) raises ValueError if arguments
        are not recognized by cRtrace.
    scene: str, optional
        path to octree
    nproc: int, optional
        if None, sets nproc to cpu count, or the RAYTRAVERSE_PROC_CAP
        environment variable

    Examples
    --------

    Basic Initialization and call::

        r = renderer.Rtrace(args, scene)
        ans = r(vecs)
        # ans.shape -> (vecs.shape[0], 1)

    If rayargs include cache files (ambient cache or photon map) be careful
    with updating sources. If you are going to swap sources, update the
    arguments as well with the new paths::

        r = renderer.Rtrace(args, scene)
        r.set_args(args.replace("temp.amb", "temp2.amb"))
        r.load_source(srcdef)

    Note that if you are using ambient caching, you must give an ambient file,
    because without a file ambient values are not shared across processes or
    successive calls to the instance.
    """
    name = 'rtrace'
    #: craytraverse.crenderer.cRtrace
    instance = rtrace_instance
    ospec = "v"

    def __setstate__(self, state):
        super().__setstate__(state)
        type(self).instance = rtrace_instance

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
        needsamb, hasamb = cls.check_amb(args)
        if len(hasamb) > 0 and not needsamb:
            args = re.sub(r' -af \S+', '', args)
        super().set_args(args, nproc)
        ospec = re.findall(r"-o\w+", cls.args)
        if len(ospec) > 0:
            cls.update_ospec(ospec[-1][2:])
        else:
            cls.update_ospec(cls.ospec)

    @classmethod
    def update_ospec(cls, vs):
        """set output of cRtrace instance

        Parameters
        ----------
        vs: str
            output specifiers for rtrace::
                o    origin (input)
                d    direction (normalized)
                v    value (radiance)
                V    contribution (radiance)
                w    weight
                W    color coefficient
                l    effective length of ray
                L    first intersection distance
                c    local (u,v) coordinates
                p    point of intersection
                n    normal at intersection (perturbed)
                N    normal at intersection (unperturbed)
                r    mirrored value contribution
                x    unmirrored value contribution
                R    mirrored ray length
                X    unmirrored ray length

        Returns
        -------
        outcnt: int
            the number of output columns to expect when calling rtrace instance

        Raises
        ------
        ValueError:
            when an output specifier is not recognized
        """
        outcnt = cls.instance.update_ospec(vs)
        if outcnt < 0:
            raise ValueError(f"Could not update {cls.__name__} with "
                             f"outputs: '{vs}'")
        cls.ospec = vs
        cls.features = outcnt
        return outcnt

    @classmethod
    def check_amb(cls, args):
        try:
            ab = re.findall(r'-ab \d+', args)[-1]
        except IndexError:
            hasbounce = False
        else:
            hasbounce = int(ab.split()[-1]) > 0
        try:
            aa = re.findall(r'-aa \d+', args)[-1]
        except IndexError:
            caching = True
        else:
            caching = int(aa.split()[-1]) > 0
        hasamb = re.findall(r'-af \S+', args)
        return hasbounce and caching, hasamb

    @classmethod
    def load_source(cls, srcfile, freesrc=-1, ambfile=None):
        """add a source description to the loaded scene

        Parameters
        ----------
        srcfile: str
            path to radiance scene file containing sources, these should not
            change the bounding box of the octree and has only been tested with
            the "source" type.
        freesrc: int, optional
            the number of objects to unload from the end of the rtrace object
            list, if -1 unloads all objects loaded by previous calls to
            load_source
        ambfile: str, optional
            path to ambient file. if given, and arguments
        """
        cls.instance.load_source(srcfile, freesrc)
        needsamb, hasamb = cls.check_amb(cls.args)
        if needsamb:
            args = re.sub(r' -af \S+', '', cls.args)
            if ambfile is not None:
                args += f" -af {ambfile}"
            elif len(hasamb) > 0:
                print("Warning: source changed with ambient caching, but "
                      f"no new ambfile was specified, stripping {hasamb[-1]} "
                      "from args", file=sys.stderr)
            cls.set_args(args)
