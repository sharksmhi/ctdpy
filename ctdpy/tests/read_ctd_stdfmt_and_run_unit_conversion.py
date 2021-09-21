# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-07-10 14:09

@author: a002028

"""
import sys
from ctdpy.core.session import Session
from ctdpy.core.utils import generate_filepaths, get_reversed_dictionary
from ctdpy.core import config, data_handlers
import time
from pprint import pprint


# GET FILES
base_dir = r'C:\Arbetsmapp\datasets\Profile\2020\SHARK_Profile_2020_NMK_SGUS\processed_data'

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
print('Files loaded:')
pprint(list(datasets[0]))


# Unit Conversion
converter = data_handlers.UnitConverter(
    s.settings.mapping_unit,
    s.settings.user
)

for data_key, item in datasets[0].items():
    converter.update_meta(item['metadata'])
    unit_converted = False
    for parameter in converter.mapper:
        if parameter in item['data']:
            unit_converted = True
            item['data'][parameter] = converter.convert_values(item['data'][parameter])

    if unit_converted:
        converter.rename_dataframe_columns(item['data'])
        converter.append_conversion_comment()


# UPDATE DATA ACCORDING TO CTD TEMPLATE (TXT-FORMAT)
# As of now we only export the updated ctd-datafile (ctd-standard-format).
# delivery_note, metadata, sensorinfo, information are exclude..

start_time = time.time()
data_path = s.save_data(datasets, writer='ctd_standard_template', return_data_path=True)
print("Datasets saved--%.3f sec" % (time.time() - start_time))
