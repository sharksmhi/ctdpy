#!/usr/bin/env python3
"""
Created on 2021-11-29 09:26

@author: johannes
"""
from ctdpy.core.session import Session
from ctdpy.core.utils import generate_filepaths, get_reversed_dictionary
from sharkpylib.qc.qc_default import QCBlueprint
import time


# GET FILES
base_dir = r'C:\Utveckling\ctdpy\ctdpy\exports\ctd_std_fmt_20211126_181359'

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

# READ DATA
datasets = s.read()


# QUALITY CONTROL
# This will produce a lot of prints...
for item in datasets[0].values():
    # FIXME missing unit in parameter names.. Fix in sensorinfo.txt before creating stdfmt.
    parameter_mapping = get_reversed_dictionary(s.settings.pmap, item['data'].keys())
    qc_run = QCBlueprint(item, parameter_mapping=parameter_mapping)
    qc_run()


# Auto QC performed. Q-flags inserted
first_ds = list(datasets[0])[0]


# UPDATE DATA ACCORDING TO CTD TEMPLATE (TXT-FORMAT)
# As of now we only export the updated ctd-datafile (ctd-standard-format).
# delivery_note, metadata, sensorinfo, information are exclude.. (will be included..)
data_path = s.save_data(datasets, writer='ctd_standard_template', return_data_path=True,
                        save_path='C:/ctdpy_exports')
