# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 08:22:21 2018

@author: a002028
"""
from ctdpy.core.session import Session
from ctdpy.core.utils import generate_filepaths


base_dir = r'C:\Utveckling\TESTING\data2sqlite\test_data'

files = generate_filepaths(
    base_dir,
    pattern_list=['.cnv', '.xlsx'],
    only_from_dir=False,
)

s = Session(
    filepaths=files,
    reader='smhi',
)

datasets = s.read()
