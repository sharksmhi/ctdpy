# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2020-10-21 19:44

@author: a002028

"""
import matplotlib.pyplot as plt
from ctdpy.core.session import Session
from ctdpy.core.utils import generate_filepaths

fid = 'C:\\Arbetsmapp\\datasets\\Profile\\2019\\SHARK_Profile_2019_SMHI\\received_data\\'
files = generate_filepaths(fid,
                           endswith='34_01_0005.cnv',
                           )

s = Session(filepaths=files,
            reader='smhi',
            )
datasets = s.read()
print("Datasets loaded")

df = datasets[0]['SBE09_0745_20190111_0929_34_01_0005.cnv']['data']
plt.plot(df['PRES_CTD'].astype(float), df['SCAN_CTD'].astype(int), '-')
plt.gca().invert_yaxis()
plt.xlabel('PRES_CTD')
plt.ylabel('SCAN_CTD')
