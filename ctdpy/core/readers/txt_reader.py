# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 10:23:06 2018

@author: a002028
"""
import pandas as pd


def load_txt(file_path='',
             seperator='\t',
             encoding='cp1252',
             fill_nan='',
             header_row=0,
             as_dtype=None,
             as_dict=False):
    """Load text file and return pandas DataFrame.

    Args:
        file_path (str): path to file
        seperator (str):
        encoding (str):
        fill_nan: str | np.nan
        header_row (int): row number
        as_dtype: str | np.float | int
        as_dict (bool): False | True
    """
    if as_dtype:
        with open(file_path, 'r') as f:
            # is .strip('\r') necessary?
            header = f.readline().strip('\n').strip('\r').split(seperator)

        df = pd.read_csv(file_path,
                         sep=seperator,
                         encoding=encoding,
                         dtype={key: str for key in header},
                         engine='python').fillna(fill_nan)
    else:
        df = pd.read_csv(file_path,
                         sep=seperator,
                         header=header_row).fillna(fill_nan)
    if as_dict:
        df = df.fillna(fill_nan)
        return {key: df[key].values for key in df.keys()}
    else:
        return df
