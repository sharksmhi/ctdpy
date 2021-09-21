# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2021-09-08 13:02

@author: johannes
"""

from ctdpy.core.session import Session
from ctdpy.core.utils import generate_filepaths

import time
from pprint import pprint


# GET FILES
base_dir = r'C:\Temp\ctdpy_temp\mw_testdata'

# Note the time difference (~ x10) when loading data from fileserver (EXPRAPP) compared to reading from local disc..
files = generate_filepaths(
    base_dir,
    endswith='.cnv',  # Only cnv-files
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
# start_time = time.time()
# datasets are stored in a list of 2 (idx 0: data, idx 1: metadata). For this example we only have data
# s.save_data(datasets[0],
#             writer='metadata_template',
#             )

print("Metadata file created--%.3f sec" % (time.time() - start_time))
