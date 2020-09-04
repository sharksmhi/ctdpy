# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 11:38:08 2018

@author: a002028

"""
import sys
import os
import json

name = "ctdpy"

package_path = os.path.dirname(os.path.realpath(__file__))
package_path = package_path.replace('ctdpy\\ctdpy', 'ctdpy')

pypaths_path = package_path + '\\pypaths.json'


def append_path_to_system(item):
    if isinstance(item, str):
        if item not in sys.path:
            if os.path.isdir(item):
                sys.path.append(item)
            else:
                print('\nWARNING! Could not add "{}" to sys.path. \n'
                      'You should probably change path to the py-package "{}" in '
                      'settingsfile: {}\n'.format(item, os.path.basename(item), pypaths_path))
    elif isinstance(item, list):
        for it in item:
            append_path_to_system(it)
    elif isinstance(item, dict):
        for k, it in item.items():
            append_path_to_system(it)


def append_python_paths():
    if os.path.isfile(pypaths_path):
        with open(pypaths_path, 'r') as fd:
            d = json.load(fd)
        append_path_to_system(d)


append_python_paths()

from ctdpy import core
