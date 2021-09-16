# -*- coding: utf-8 -*-
"""
Created on 2020-02-18 13:42

@author: a002028

"""
import time
from ctdpy.core.session import Session
from ctdpy.core import config
from ctdpy.core.utils import get_file_list_based_on_suffix, generate_filepaths, match_filenames


base_dir = '...Svea v6-7 Feb\\mvp\\cnv'

# files = os.listdir(base_dir)
files = generate_filepaths(base_dir,
                           # pattern_list=['.TOB', '.xlsx'],
                           endswith='.cnv',
                           only_from_dir=True)

start_time = time.time()
s = Session(filepaths=files,
            reader='smhi',
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
datasets = s.read()
print("Datasets loaded--%.3f sec" % (time.time() - start_time))

#  -----------------------------------------------------------------------------------------------------------------
#  ##################        SAVE DATA ACCORDING TO CTD TEMPLATE (TXT-FORMAT)        ###################
start_time = time.time()
data_path = s.save_data(datasets, writer='ctd_standard_template', return_data_path=True)
print("Datasets saved--%.3f sec" % (time.time() - start_time))

#  -----------------------------------------------------------------------------------------------------------------
#  ###################        CREATE ARCHIVE        ###################
# start_time = time.time()
# s.create_archive(data_path=data_path)
# print("Archive created--%.3f sec" % (time.time() - start_time))

#  -----------------------------------------------------------------------------------------------------------------
#  ###################        TEST PRINTS        ###################
# from calculator import Calculator
# import numpy as np
# attr_dict = {'latitude': datasets[0]['SBE09_1044_20181205_1536_34_01_0154.cnv']['metadata']['LATIT'],
#              'pressure': datasets[0]['SBE09_1044_20181205_1536_34_01_0154.cnv']['hires_data']['PRES_CTD'].astype(np.float),
#              'gravity': datasets[0]['SBE09_1044_20181205_1536_34_01_0154.cnv']['hires_data']['PRES_CTD'].astype(np.float),
#              'density': datasets[0]['SBE09_1044_20181205_1536_34_01_0154.cnv']['hires_data']['DENS_CTD'].astype(np.float)}
# calc_obj = Calculator()
# td = calc_obj.get_true_depth(attribute_dictionary=attr_dict)
# res_head = 'hires_data'
# res_head = 'lores_data_all'
# print(datasets[0].keys())
# print(datasets[1].keys())
# print(datasets[1]['CTD Profile ifylld.xlsx']['Metadata'].keys())
# print(datasets[0]['SBE09_1044_20181205_1536_34_01_0154.cnv'].keys())
# print(datasets[0]['SBE09_1044_20181205_1536_34_01_0154.cnv']['metadata'].keys())
# print(datasets[0]['SBE09_1044_20181205_1536_34_01_0154.cnv'][res_head].keys())
# pprint(datasets[0].keys())
# print(datasets[0]['SBE09_1044_20181205_1536_34_01_0154.cnv']['metadata']['FILENAME'])
#  -----------------------------------------------------------------------------------------------------------------
#  ###################        WRITE METADATA TO TEMPLATE        ###################
start_time = time.time()
s.save_data(datasets[0], writer='metadata_template')
print("Metadata file created--%.3f sec" % (time.time() - start_time))

#  -----------------------------------------------------------------------------------------------------------------
# TODO läsare med alt. för fler flagfält
# TODO skrivare med alt. för fler Q-flags-fält per parameter

# pprint(s.settings.templates)
# pprint(s.settings.writers['ctd_standard_template']['writer'])
# pprint(type(datasets[0]['Test_Leveransmall_CTD.xlsx']['Sensorinfo'].columns))
# import pandas as pd
# print(datasets[0]['SBE09_0827_20180120_0910_26_01_0126.cnv']['hires_data']['TEMP_CTD'].values)
# datasets[1]['Test_Leveransmall_CTD.xlsx']['Sensorinfo'].pop('Tabellhuvud:')
# print(datasets[1]['Test_Leveransmall_CTD.xlsx']['Information'])
# f = pd.Series(datasets[1]['Test_Leveransmall_CTD.xlsx']['Sensorinfo'].columns)
# print(f)
# print(f.str.cat(sep='\t'))
# for dset in datasets:
#     print(dset.keys())
# FIXME "datasets[0]" the list should me merged before given from session.read(add_merged_data=True)
# template_data = s.get_data_in_template(datasets[0], writer='xlsx', template='phyche')
# pprint(template_data)
# s.save_data(template_data)
