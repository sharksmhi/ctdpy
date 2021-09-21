# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-07-10 13:59

@author: a002028

"""
from ctdpy.core.session import Session
from ctdpy.core.utils import generate_filepaths, get_reversed_dictionary
import time
from pprint import pprint


# GET FILES
# base_dir = '...\\Svea_v16 april\\CTD\\data'  # tar längre tid att läsa ifrån filtjänst
base_dir = r'C:\Utveckling\ctdpy\ctdpy\tests\test_data\exprapp_april_2020'

files = generate_filepaths(
    base_dir,
    # pattern_list=['.cnv', '.xlsx'],  # Both cnv- and metadata-files
    endswith='.cnv',  # Only cnv-files
    # endswith='.txt',  # Presumably CTD-standard format
    only_from_dir=True,  # we exclude search of files from folders under "base_dir"
)

# Create SESSION object
s = Session(
    filepaths=files,
    reader='smhi',
)

# READ DELIVERY DATA, CNV, XLSX
start_time = time.time()
datasets = s.read()
print("Datasets loaded--%.3f sec" % (time.time() - start_time))
print('Files loaded:')
pprint(list(datasets[0].keys()))


# WRITE METADATA TO TEMPLATE
# datasets are stored in a list of 2 (idx 0: data, idx 1: metadata). For this example we only have data
start_time = time.time()
s.save_data(
    datasets[0],
    writer='metadata_template',
)

print("Metadata file created--%.3f sec" % (time.time() - start_time))
