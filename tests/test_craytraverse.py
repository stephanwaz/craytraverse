#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for raytraverse.craytraverse"""
from craytraverse.craytraverse import from_pdf
import numpy as np


def test_from_pdf():
    nsamp = 500000
    threshold = .3
    lb = 0.5
    ub = 4
    pdf = np.linspace(0, 1, nsamp)
    exp = np.sum(pdf > threshold)
    
    candidates, bidx, nsampc = from_pdf(pdf, threshold, lb=lb, ub=ub+1)
    if nsampc == 0:
        return bidx
    pdfc = pdf[candidates]/np.sum(pdf[candidates])
    cidx = np.random.default_rng().choice(candidates, nsampc,
                                          replace=False, p=pdfc)
    c = np.concatenate((bidx, cidx))
    assert np.isclose(c.size, exp)
