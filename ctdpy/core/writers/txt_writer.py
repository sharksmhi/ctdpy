# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 13:38:35 2018

@author: a002028
"""
import numpy as np
from ctdpy.core.utils import thread_process


class TxtWriter:
    """Writer of text files."""

    def __init__(self, in_template=None):
        """Initialize and store in_template.

        Args:
            in_template:
        """
        # TODO Is self.in_template ever used?
        self.in_template = in_template

    @staticmethod
    def write_with_pandas(data=None,
                          save_path=None,
                          header=False,
                          sep='\t',
                          encoding='cp1252'):
        """Write dataframe or serie.

        Args:
            data: pd.DataFrame, pd.Series
            save_path (str): complete path to file
            header (bool): True / False. Include header.
            sep (str): separator
            encoding (str): Encoding to use when writing
        """
        data.to_csv(save_path, sep=sep, encoding=encoding, index=False, header=header)

    @staticmethod
    def write_with_numpy(data=None, save_path=None, fmt='%s'):
        """Write numpy arrays or pd.Series to file.

        Args:
            data: array
            save_path (str): complete path to file
            fmt: format of file eg. '%s', '%f'
        """
        thread_process(np.savetxt, save_path, data, fmt=fmt)

    @staticmethod
    def write_with_python(data=None, save_path=None):
        """Write with the python open method."""
        raise NotImplementedError
