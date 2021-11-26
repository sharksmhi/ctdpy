#!/usr/bin/env python3
"""
Created on 2021-11-26 13:51

@author: johannes
"""
from ctdpy.core.session import Session
from ctdpy.core.utils import generate_filepaths, get_reversed_dictionary
from sharkpylib.qc.qc_default import QCBlueprint
import time


# GET FILES
base_dir = r'C:\Temp\CTD_DV\test_txt_meta_fmt'

files = generate_filepaths(
    base_dir,
    pattern_list=['.cnv', '.txt'],  # Both cnv- and metadata-files
    only_from_dir=True,  # we exclude search of files from folders under "base_dir"
)

# Create SESSION object
s = Session(
    filepaths=files,
    reader='smhi',
)

datasets = s.read()
print(list(datasets[1]))
for df in datasets[1].values():
    print(df)
