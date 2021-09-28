# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 08:22:21 2018

@author: a002028
"""
import time
from pprint import pprint
from ctdpy.core.session import Session
from ctdpy.core.utils import generate_filepaths


base_dir = r'C:\Temp\CTD_DV\ctd_data_sep2021'

files = generate_filepaths(
    base_dir,
    endswith='.cnv',
)

start_time = time.time()
s = Session(
    filepaths=files,
    reader='smhi',
)

print("Session--%.3f sec" % (time.time() - start_time))
# ###################        TEST PRINTS        ###################
# print('SHIPmapping test', s.settings.smap.map_cntry_and_shipc(cntry='34', shipc='AR'))
# print('SHIPmapping test', s.settings.smap.map_shipc('3401'))
# print('SHIPmapping test', s.settings.smap.map_shipc('Aranda'))
# pprint(s.settings.templates['ctd_metadata'])
# pprint(s.settings.settings_paths)

#  ###################        READ DELIVERY DATA, CNV, XLSX        ###################
start_time = time.time()
# FIXME "datasets[0]" the list should me merged before given from session.read(add_merged_data=True)
# datasets = s.read(add_merged_data=True, add_low_resolution_data=True)
# datasets = s.read(add_merged_data=True)
datasets = s.read()
print("Datasets loaded--%.3f sec" % (time.time() - start_time))
print(len(datasets[0].keys()))
pprint(list(datasets[0].keys()))
