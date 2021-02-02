# -*- coding: utf-8 -*-
"""
Created on 2021-02-02 11:29
@author: johannes
"""


import pandas as pd
from ctdpy.core import utils

file_path = 'C:/Utveckling/ctdpy/ctdpy/templates/Format Profile.xlsx'

xlxs = pd.ExcelFile(file_path)

df = xlxs.parse(
    'Förklaring',
    header='None',
    # dtype=str,
    # keep_default_na=False,
)
