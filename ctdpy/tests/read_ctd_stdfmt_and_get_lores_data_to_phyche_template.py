# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-07-10 14:15

@author: a002028
"""
from ctdpy.core.session import Session
from ctdpy.core.utils import generate_filepaths
from pprint import pprint


base_dir = r'C:\Arbetsmapp\datasets\Profile\2020\SHARK_Profile_2020_COD_SMHI\processed_data'
files = generate_filepaths(
    base_dir,
    endswith='.txt',  # Presumably CTD-standard format
    only_from_dir=False,
)

s = Session(
    filepaths=files,
    reader='ctd_stdfmt',
)

datasets = s.read()
print('Files loaded:')
pprint(list(datasets[0]))

template = s.get_data_in_template(datasets[0], template='phyche', resolution='lores')

# data_path = s.save_data(
#     datasets,
#     writer='ctd_standard_template',
#     return_data_path=True,
#     save_path='C:/ctdpy_exports',
# )
