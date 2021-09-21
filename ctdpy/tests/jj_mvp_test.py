# -*- coding: utf-8 -*-
"""
Created on 2020-02-18 13:42

@author: a002028

"""
import time
from ctdpy.core.session import Session
from ctdpy.core import config
from ctdpy.core.utils import get_file_list_based_on_suffix, generate_filepaths, match_filenames


base_dir = r'...Svea v6-7 Feb/mvp/cnv'
files = generate_filepaths(
    base_dir,
    # pattern_list=['.TOB', '.xlsx'],
    endswith='.cnv',
    only_from_dir=True
)

start_time = time.time()
s = Session(
    filepaths=files,
    reader='smhi',
)
print("Session--%.3f sec" % (time.time() - start_time))
# TEST PRINTS
# print('SHIPmapping test', s.settings.smap.map_cntry_and_shipc(cntry='34', shipc='AR'))
# print('SHIPmapping test', s.settings.smap.map_shipc('3401'))
# print('SHIPmapping test', s.settings.smap.map_shipc('Aranda'))
# print('SHIPmapping test', s.settings.smap.map_shipc('ARANDA'))
# pprint(s.settings.templates['ctd_metadata'])
# pprint(s.settings.settings_paths)

# READ DELIVERY DATA, CNV, XLSX
start_time = time.time()
# # FIXME "datasets[0]" the list should me merged before given from session.read(add_merged_data=True)
# datasets = s.read(add_merged_data=True, add_low_resolution_data=True)
datasets = s.read()
print("Datasets loaded--%.3f sec" % (time.time() - start_time))

# SAVE DATA ACCORDING TO CTD TEMPLATE (TXT-FORMAT)
start_time = time.time()
data_path = s.save_data(datasets, writer='ctd_standard_template', return_data_path=True)
print("Datasets saved--%.3f sec" % (time.time() - start_time))

# CREATE ARCHIVE
# start_time = time.time()
# s.create_archive(data_path=data_path)
# print("Archive created--%.3f sec" % (time.time() - start_time))
