# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-07-10 14:15

@author: a002028
"""
from ctdpy.core.session import Session
from ctdpy.core.utils import generate_filepaths, get_reversed_dictionary
from profileqc.qc import SessionQC
import time


# GET FILES
base_dir = r'C:\Arbetsmapp\datasets\Profile\2020\SHARK_Profile_2020_COD_SMHI\processed_data'

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

# READ DELIVERY DATA, CNV, XLSX
start_time = time.time()
datasets = s.read()
print("Datasets loaded--%.3f sec" % (time.time() - start_time))
# print('Files loaded:')
# pprint(list(datasets[0]))


# QUALITY CONTROL
start_time = time.time()

# This will produce alot of prints...
for item in datasets[0].values():
    parameter_mapping = get_reversed_dictionary(s.settings.pmap, item['data'].keys())
    qc_run = SessionQC(item, parameter_mapping=parameter_mapping)
    qc_run.run()

print("QCBlueprint run--%.3f sec" % (time.time() - start_time))

# Auto QC performed. Q-flags inserted
first_ds = list(datasets[0])[0]

print('Note format of flagfield')
# print(datasets[0][first_ds]['data']['Q0_TEMP_CTD'][:5])
# print('\nDataframe from file: {}'.format(first_ds))
# print(datasets[0][first_ds]['metadata'])


# UPDATE DATA ACCORDING TO CTD TEMPLATE (TXT-FORMAT)
# As of now we only export the updated ctd-datafile (ctd-standard-format).
# delivery_note, metadata, sensorinfo, information are exclude.. (will be included..)

start_time = time.time()
data_path = s.save_data(datasets, writer='ctd_standard_template', return_data_path=True, save_path='C:/ctdpy_exports')
print("Datasets saved--%.3f sec" % (time.time() - start_time))
