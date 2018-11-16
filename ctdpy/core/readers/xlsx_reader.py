# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 13:22:24 2018

@author: a002028
"""

import pandas as pd

#==============================================================================

def load_excel(f_name=u'', sheet_name='Data', header_row=0):
    """
    :param f_name: str
    :param sheet_name: str
    :param header_row: int
    :return: pd.DataFrame
    """
    # get number of columns
    xl = pd.ExcelFile(f_name)
    ncols = xl.book.sheet_by_name(sheet_name).ncols
    xl.close()
    #empty cells will be loaded as np.nan
    # Python 3: use str instead of unicode
    return pd.read_excel(f_name, sheet_name=sheet_name, header=header_row,
                         converters={i: str for i in range(ncols)})

#==============================================================================