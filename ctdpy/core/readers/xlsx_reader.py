# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 13:22:24 2018

@author: a002028
"""
import pandas as pd
from ctdpy.core import utils


def load_excel(file_path='', sheet_name=None, header_row=None):
    """Load excel file with pandas."""
    xlxs = pd.ExcelFile(file_path)

    if utils.is_sequence(sheet_name):
        sheets = {}
        for sheet, h_row in zip(sheet_name, header_row):
            sheets[sheet] = xlxs.parse(
                sheet,
                header=h_row,
                dtype=str,
                keep_default_na=False
            )
        return sheets
    else:
        return xlxs.parse(
            sheet_name,
            header=header_row,
            dtype=str,
            keep_default_na=False
        )
