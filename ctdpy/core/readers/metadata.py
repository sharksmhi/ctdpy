# -*- coding: utf-8 -*-
"""
Created on 2019-11-04 10:37

@author: a002028

"""
""" Metadata reader
"""
import sys
sys.path.append("..")
from core.utils import get_filename
from core.data_handlers import DataFrameHandler
from core.data_handlers import BaseReader
from core.readers.xlsx_reader import load_excel


class XLSXmeta(BaseReader, DataFrameHandler):
    """
    """
    def __init__(self, settings):
        super().__init__(settings)
        self.data = {}
        self.file_specs = None

    def get_data(self, filenames=None, add_low_resolution_data=False):
        """
        :param filenames: list of file paths
        :return: Dictionary with DataFrames
        """
        reader = self.get_reader_instance()
        for file_path in filenames:
            fid = get_filename(file_path)
            self.data[fid] = {}
            self._read(file_path, self.file_specs, reader, self.data[fid])

        return self.data

    def merge_data(self, data, resolution=None):
        """
        :param data: data
        :param resolution: None
        :return: pass
        """
        pass

    @staticmethod
    def _read(file_path, file_specs, reader, data):
        """
        :param file_path: str
        :param file_specs: Dictionary
        :param reader: Reader instance
        :param data: Dictionary
        :return: Updates data
        """
        for sheet_name, header_row in zip(file_specs['sheet_names'], file_specs['header_rows']):
            df = reader(file_path=file_path,
                        sheet_name=sheet_name,
                        header_row=header_row)
            data[sheet_name] = df.fillna('')

    @staticmethod
    def get_reader_instance():
        """
        Could be done differently
        :return: Reader instance
        """
        return load_excel
