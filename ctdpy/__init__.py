# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 11:38:08 2018

@author: a002028
"""

"""
"""
from . import core
from . import tests
import config
from .config import Settings
import sys
import os

package_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(package_path)

name = "ctdpy"