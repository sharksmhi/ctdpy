# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 13:22:24 2018

@author: a002028
"""

import pandas as pd
from utils import is_sequence


def load_excel(file_path='', sheet_name=None, header_row=None):
    """
    :param file_path: str
    :param sheet_name: str, list
    :param header_row: int, list
    :return: pd.DataFrame / dict with pd.DataFrames
    """
    # print(file_path, sheet_name, header_row)
    def read_sheet(sheet, h_row, ncols):
        return pd.read_excel(xlxs, sheet_name=sheet, header=h_row,
                             converters={i: str for i in range(ncols)})

    xlxs = pd.ExcelFile(file_path)

    if is_sequence(sheet_name):
        sheets = {}
        for sheet, h_row in zip(sheet_name, header_row):
            sheets[sheet] = read_sheet(sheet, h_row,
                                       xlxs.book.sheet_by_name(sheet).ncols)
        return sheets
    else:
        return read_sheet(sheet_name, header_row,
                          xlxs.book.sheet_by_name(sheet_name).ncols)
