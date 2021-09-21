# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2021-04-19 10:22

@author: johannes
"""
from ctdpy.core.session import Session
from ctdpy.core.utils import generate_filepaths, get_reversed_dictionary


base_dir = r'C:\Temp\CTD_DV\SGU\SGU_upp20_profile_rapportering_20210401'

files = generate_filepaths(
    base_dir,
    pattern_list=['.vp2', '.xlsx'],  # Both cnv- and metadata-files
)

s = Session(filepaths=files, reader='sgus')
datasets = s.read()

data_path = s.save_data(
    datasets,
    writer='ctd_standard_template',
    return_data_path=True,
)

s.create_archive(data_path=data_path)
