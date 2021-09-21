# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-07-10 14:05

@author: a002028

"""
from ctdpy.core.session import Session
from ctdpy.core.utils import generate_filepaths
import time
from pprint import pprint


base_dir = r'C:\Utveckling\ctdpy\ctdpy\tests\test_data\exprapp_april_2020'

# only_from_dir=False: We accept filesearch from folders within base_dir,
# only_from_dir=True: We only accept filesearch base_dir, not from folders within base_dir
files = generate_filepaths(
    base_dir,
    pattern_list=['.cnv', '.xlsx'],  # Both cnv- and metadata-files
    only_from_dir=False,
)

# Create SESSION object
start_time = time.time()
s = Session(
    filepaths=files,
    reader='smhi',
)
print("Session--%.3f sec" % (time.time() - start_time))

# READ DELIVERY DATA, CNV, XLSX
start_time = time.time()
datasets = s.read()
print("Datasets loaded--%.3f sec" % (time.time() - start_time))
print('Files loaded:')

# if IntexError, the metadata template has not been loaded:
# Check setup of file-generator (which should include both 'cnv' and 'xlsx')
pprint(list(datasets[1].keys()))
pprint(list(datasets[0].keys()))

# SAVE DATA ACCORDING TO CTD STANDARD FORMAT (TXT)
# start_time = time.time()
data_path = s.save_data(
    datasets,
    writer='ctd_standard_template',
    return_data_path=True,
)
# print("Datasets saved--%.3f sec\n" % (time.time() - start_time))
# print('Path to saved data: \n{}'.format(data_path))
