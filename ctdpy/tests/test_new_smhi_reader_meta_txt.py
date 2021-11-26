#!/usr/bin/env python3
"""
Created on 2021-11-26 13:51

@author: johannes
"""
from ctdpy.core.session import Session
from ctdpy.core.utils import generate_filepaths


# GET FILES
base_dir = r'C:\Temp\CTD_DV\test_txt_meta_fmt'

files = generate_filepaths(base_dir, pattern_list=['.cnv', '.txt'])

# Create SESSION object
s = Session(
    filepaths=files,
    reader='smhi',
)

datasets = s.read()
print(list(datasets[0]))
print(list(datasets[1]))

# SAVE DATA ACCORDING TO CTD STANDARD FORMAT (TXT), but "keep_original_file_names"
data_path = s.save_data(
    datasets,
    writer='ctd_standard_template',
    keep_original_file_names=True,
    return_data_path=True,
)
print('Path to saved data: {}'.format(data_path))
