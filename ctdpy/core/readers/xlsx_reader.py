# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 13:22:24 2018

@author: a002028
"""

import pandas as pd
from ctdpy.core import utils


def load_excel(file_path='', sheet_name=None, header_row=None):
    """
    :param file_path: str
    :param sheet_name: str, list
    :param header_row: int, list
    :return: pd.DataFrame / dict with pd.DataFrames
    """
    xlxs = pd.ExcelFile(file_path)

    if utils.is_sequence(sheet_name):
        sheets = {}
        for sheet, h_row in zip(sheet_name, header_row):
            xlxs.parse(
                sheet,
                header=header_row,
                dtype=str,
                keep_default_na=False,
            )
        return sheets
    else:
        return xlxs.parse(
                sheet_name,
                header=header_row,
                dtype=str,
                keep_default_na=False,
            )
