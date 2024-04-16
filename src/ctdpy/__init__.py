#!/usr/bin/env python3
"""
Created on Thu Jul 05 11:38:08 2018

@author: a002028
"""
from pkg_resources import get_distribution, DistributionNotFound


try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

from ctdpy import core  # noqa: F401
name = "ctdpy"
