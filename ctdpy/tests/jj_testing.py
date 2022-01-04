# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 08:22:21 2018

@author: a002028
"""
from ctdpy.core.session import Session
from ctdpy.core.utils import generate_filepaths


base_dir = r'C:\Temp\CTD_DV\qc_DEEP_2020\data'

files = generate_filepaths(
    base_dir,
    pattern_list=['.TOB', '.xlsx'],
    only_from_dir=False,
)

s = Session(
    filepaths=files,
    reader='deep',
)

datasets = s.read()

# data_path = s.save_data(datasets, writer='ctd_standard_template',
#                         return_data_path=True, save_path='C:/ctdpy_exports')
