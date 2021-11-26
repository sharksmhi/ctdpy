# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 08:22:21 2018

@author: a002028
"""
from ctdpy.core.session import Session
from ctdpy.core.utils import generate_filepaths, get_reversed_dictionary
from sharkpylib.qc.qc_default import QCBlueprint
import time
from pprint import pprint


# GET FILES
base_dir = r'C:\Temp\CTD_DV\mw_test'

files = generate_filepaths(
    base_dir,
    endswith='.txt',  # Presumably CTD-standard format
    only_from_dir=False,
)

# Create SESSION object
s = Session(
    filepaths=files,
    reader='ctd_stdfmt',
)
datasets = s.read()

# This will produce alot of prints...
for item in datasets[0].values():
    parameter_mapping = get_reversed_dictionary(s.settings.pmap, item['data'].keys())
    qc_run = QCBlueprint(item, parameter_mapping=parameter_mapping)
    qc_run()


# Auto QC performed. Q-flags inserted
first_ds = list(datasets[0])[0]

print('Note format of flagfield')
print(datasets[0][first_ds]['data']['Q0_TEMP_CTD'][:5])
print('\nDataframe from file: {}'.format(first_ds))
print(datasets[0][first_ds]['metadata'])


# UPDATE DATA ACCORDING TO CTD TEMPLATE (TXT-FORMAT)
# As of now we only export the updated ctd-datafile (ctd-standard-format).
# delivery_note, metadata, sensorinfo, information are exclude.. (will be included..)

start_time = time.time()
data_path = s.save_data(datasets, writer='ctd_standard_template', return_data_path=True, save_path='C:/ctdpy_exports')
print("Datasets saved--%.3f sec" % (time.time() - start_time))
