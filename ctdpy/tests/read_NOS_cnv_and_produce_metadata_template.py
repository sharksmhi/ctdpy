# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-07-10 13:59

@author: a002028

"""
from ctdpy.core.session import Session
from ctdpy.core.utils import generate_filepaths
import time
from pprint import pprint


base_dir = r'C:\Temp\CTD_DV\qc_NOS_2015\data'
files = generate_filepaths(
    base_dir,
    pattern_list=['.cnv', '.xlsx'],
)

s = Session(
    filepaths=files,
    reader='nos',
)
datasets = s.read()
print('Files loaded:')
pprint(list(datasets[0].keys()))

# s.save_data(
#     datasets[0],
#     writer='metadata_template',
# )
# data_path = s.save_data(
#     datasets,
#     writer='ctd_standard_template',
#     return_data_path=True,
# )