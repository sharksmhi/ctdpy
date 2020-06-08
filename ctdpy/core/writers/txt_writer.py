# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 13:38:35 2018

@author: a002028
"""

# from core.writers.with_style import with_style
import csv
import numpy as np
from ctdpy.core.utils import thread_process


class TxtWriter(object):
    """ """
    def __init__(self, in_template=None):
        self.in_template = in_template

    @staticmethod
    def write_with_pandas(data=None,
                          save_path=None,
                          header=False,
                          sep='\t',
                          # encoding='utf-8'):
                          encoding='cp1252'):
        """
        Writes dataframe or series
        :param data: pd.DataFrame, pd.Series
        :param save_path: complete path to file
        :param header: Include header in file
        :param sep: Row separator
        :param encoding: Encoding of out file
        :return: Text file
        """
        # print('pandas', save_path)
        data.to_csv(save_path, sep=sep, encoding=encoding, index=False, header=header)

    @staticmethod
    def write_with_numpy(data=None, save_path=None, fmt='%s'):
        """
        Writes numpy arrays or pd.Series
        :param data: array
        :param save_path: complete path to file
        :param fmt: format of file e.g. s:str, f:float
        :return: Text file
        """
        # print('numpy', save_path)
        thread_process(np.savetxt, save_path, data, fmt=fmt)
        # np.savetxt(save_path, data, fmt=fmt)

    @staticmethod
    def write_with_python(data=None, save_path=None):
        """
        :param data:
        :param save_path:
        :return:
        """
        # open(save_path, "wb").write('\n'.join(data))
        raise NotImplementedError
















