# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 10:23:06 2018

@author: a002028
"""
import pandas as pd


def load_txt(file_path='',
             separator='\t',
             encoding='cp1252',
             fill_nan='',
             header_row=0,
             as_dtype=None,
             as_dict=False):
    """Load text file and return pandas DataFrame.

    Args:
        file_path (str): path to file
        separator (str):
        encoding (str):
        fill_nan: str | np.nan
        header_row (int): row number
        as_dtype: str | np.float | int
        as_dict (bool): False | True
    """
    # FIXME Once everyboy starts using python >= 3.7 we´ll rewrite this reader.
    if as_dtype:
        with open(file_path, 'r') as f:
            # is .strip('\r') necessary?
            header = f.readline().strip('\n').strip('\r').split(separator)

        df = pd.read_csv(file_path,
                         sep=separator,
                         header=header_row,
                         encoding=encoding,
                         dtype={key: str for key in header},
                         engine='python').fillna(fill_nan)
    else:
        df = pd.read_csv(file_path,
                         sep=separator,
                         header=header_row).fillna(fill_nan)
    if as_dict:
        df = df.fillna(fill_nan)
        return {key: df[key].values for key in df.keys()}
    else:
        return df


if __name__ == "__main__":
    df = load_txt(
        file_path=r'C:\Temp\CTD_DV\test_txt_meta_fmt\delivery_note.txt',
        header_row=None,
        separator='DUMMY_SEPERATOR',
        as_dtype=str
    )
