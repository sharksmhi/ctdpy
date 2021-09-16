# -*- coding: utf-8 -*-
"""
Created on 2019-11-04 10:37

@author: a002028

"""
""" Metadata reader
"""
from ctdpy.core.utils import get_filename, thread_process, eliminate_empty_rows
from ctdpy.core.data_handlers import DataFrameHandler
from ctdpy.core.data_handlers import BaseReader
from ctdpy.core.readers.xlsx_reader import load_excel


class XLSXmeta(BaseReader, DataFrameHandler):
    """
    """
    def __init__(self, settings):
        super().__init__(settings)
        # self.data = {}
        self.file_specs = None

    def get_data(self, filenames=None, add_low_resolution_data=False):
        """
        :param filenames: list of file paths
        :return: Dictionary with DataFrames
        """
        print(self.__class__.__name__)
        data = {}
        reader = self.get_reader_instance()
        for file_path in filenames:
            # print('file_path', file_path)
            fid = get_filename(file_path)
            data[fid] = {}
            # print('before _read')
            self._read(file_path, self.file_specs, reader, data[fid])

        print('DONE XLSXmeta')
        return data

    def merge_data(self, data, resolution=None):
        """
        :param data: data
        :param resolution: None
        :return: pass
        """
        pass

    def _read(self, file_path, file_specs, reader, data):
        """
        :param file_path: str
        :param file_specs: Dictionary
        :param reader: Reader instance
        :param data: Dictionary
        :return: Updates data
        """
        for sheet_name, header_row in zip(file_specs['sheet_names'], file_specs['header_rows']):
            # print(sheet_name, header_row)

            # thread_process(self.load_func, file_path, sheet_name, header_row, data, reader)
            df = reader(
                file_path=file_path,
                sheet_name=sheet_name,
                header_row=header_row,
            )
            df = eliminate_empty_rows(df)
            data[sheet_name] = df.fillna('')

    @staticmethod
    def load_func(file_path, sheet_name, header_row, data, reader):
        df = reader(
            file_path=file_path,
            sheet_name=sheet_name,
            header_row=header_row,
        )
        df = eliminate_empty_rows(df)
        data[sheet_name] = df.fillna('')

    @staticmethod
    def get_reader_instance():
        """
        Could be done differently
        :return: Reader instance
        """
        return load_excel
