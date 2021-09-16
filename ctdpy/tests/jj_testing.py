# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 08:22:21 2018

@author: a002028
"""
import sys
sys.path.append('C:\\Utveckling\\sharkpylib')
import time
from pprint import pprint
from ctdpy.core.session import Session
from ctdpy.core import config, data_handlers
from ctdpy.core.archive_handler import Archive
from sharkpylib.qc.qc_default import QCBlueprint
from ctdpy.core.utils import get_file_list_based_on_suffix, generate_filepaths, get_reversed_dictionary, match_filenames


# base_dir = 'C:\\Utveckling\\ctdpy\\ctdpy\\tests\\etc\\data_aranda'
# base_dir = 'C:\\Utveckling\\ctdpy\\ctdpy\\tests\\etc\\exprapp_feb_2020'
# base_dir = 'C:\\Utveckling\\ctdpy\\ctdpy\\tests\\etc\\exprapp_april_2020'
# base_dir = 'C:\\Utveckling\\ctdpy\\ctdpy\\tests\\etc\\ctd_std_fmt_expedition_april_2020'
# base_dir = 'C:\\Utveckling\\ctdpy\\ctdpy\\tests\\etc\\ctd_std_fmt_QC_done_exprapp_april_2020'

# base_dir = 'C:\\Utveckling\\ctdpy\\ctdpy\\exports\\20200304_152042'
# base_dir = 'C:\\Temp\\CTD_DV\\SMHI_2018\\resultat\\archive_20191121_122431\\processed_data'
# base_dir = 'C:\\Temp\\CTD_DV\\SMF_2018\\original'
# base_dir = 'C:\\Temp\\CTD_DV\\SMHI_2018\\original'
# base_dir = 'C:\\Temp\\CTD_DV\\exp_june_2020'
base_dir = 'C:\\Temp\\CTD_DV\\ctd_std_fmt_exp_june_2020'
# base_dir = 'C:\\Arbetsmapp\\datasets\\Profile\\2018\\SHARK_Profile_2018_BAS_SMHI\\processed_data'
# base_dir = 'C:\\Temp\\CTD_DV\\SMHI_2018\\test'
# base_dir = 'C:\\Utveckling\\ctdpy\\ctdpy\\tests\\test_data'
# base_dir = 'C:\\Temp\\CTD_DV\\UMF_2018\\arbetsmapp'
# base_dir = 'C:\\Utveckling\\ctdpy\\ctdpy\\exports\\archive_20200312_132344\\processed_data'

# files = os.listdir(base_dir)
files = generate_filepaths(base_dir,
                           # pattern_list=['.TOB', '.xlsx'],
                           # pattern_list=['.cnv', '.xlsx'],
                           # endswith='.cnv',
                           endswith='.txt',
                           # only_from_dir=False,
                           )

start_time = time.time()
s = Session(filepaths=files,
            # reader='deep',
            # reader='smhi',
            # reader='umsc',
            reader='ctd_stdfmt',
            )
print("Session--%.3f sec" % (time.time() - start_time))
#  -----------------------------------------------------------------------------------------------------------------
#  ###################        TEST PRINTS        ###################
# print('SHIPmapping test', s.settings.smap.map_cntry_and_shipc(cntry='34', shipc='AR'))
# print('SHIPmapping test', s.settings.smap.map_shipc('3401'))
# print('SHIPmapping test', s.settings.smap.map_shipc('Aranda'))
# print('SHIPmapping test', s.settings.smap.map_shipc('ARANDA'))
# pprint(s.settings.templates['ctd_metadata'])
# pprint(s.settings.settings_paths)

#  -----------------------------------------------------------------------------------------------------------------
#  ###################        READ DELIVERY DATA, CNV, XLSX        ###################
start_time = time.time()
# # FIXME "datasets[0]" the list should me merged before given from session.read(add_merged_data=True)
# datasets = s.read(add_merged_data=True, add_low_resolution_data=True)
# datasets = s.read(add_merged_data=True)
datasets = s.read()
print("Datasets loaded--%.3f sec" % (time.time() - start_time))
# try:
#     pprint(list(datasets[1].keys()))
# except:
#     pass
print(len(datasets[0].keys()))
pprint(list(datasets[0].keys()))
