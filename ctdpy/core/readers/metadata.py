# -*- coding: utf-8 -*-
"""
Created on 2019-11-04 10:37

@author: a002028

"""
from ctdpy.core.data_handlers import BaseReader
from ctdpy.core.data_handlers import DataFrameHandler
from ctdpy.core.readers.txt_reader import load_txt
from ctdpy.core.readers.xlsx_reader import load_excel
from ctdpy.core.utils import (
    get_filename,
    # thread_process,
    eliminate_empty_rows
)


class TXTmeta(BaseReader, DataFrameHandler):
    """Base Class reader for SMHI datahost text file oriented CTD metadata."""

    def __init__(self, settings):
        """Initialize."""
        super().__init__(settings)
        self.file_specs = None

    def get_data(self, filenames=None, **kwargs):
        """Get metadata.

        Args:
            filenames (iterable): A sequence of files that will be used to load data from.
        """
        data = {}
        for file_path in filenames:
            fid = get_filename(file_path)
            file_specs = self.file_specs.get(fid.replace('.txt', ''))
            self._read(file_path, file_specs, data, fid)
        return data

    def _read(self, file_path, file_specs, data, fid):
        """Read txt file and store content.

        Args:
            file_path (str): Path to file
            file_specs (dict): Settings for reader
            data (dict): Data
            fid (str): file name
        """
        df = load_txt(
            file_path=file_path,
            as_dtype=str,
            **file_specs
        )
        data[fid] = eliminate_empty_rows(df)


class XLSXmeta(BaseReader, DataFrameHandler):
    """Base Class reader for SMHI datahost excel template for CTD metadata."""

    def __init__(self, settings):
        """Initialize."""
        super().__init__(settings)
        self.file_specs = None

    def get_data(self, filenames=None, **kwargs):
        """Get metadata.

        Args:
            filenames (iterable): A sequence of files that will be used to load data from.
        """
        data = {}
        reader = self.get_reader_instance()
        for file_path in filenames:
            fid = get_filename(file_path)
            data[fid] = {}
            self._read(file_path, self.file_specs, reader, data[fid])
        return data

    def merge_data(self, data, resolution=None):
        """Merge data."""
        # Not used when we only have metadata.
        pass

    def _read(self, file_path, file_specs, reader, data):
        """Read one sheet at a time.

        Args:
            file_path (str): Path to file
            file_specs (dict): Settings for reader
            reader (obj): Reader instance
            data (dict): Data
        """
        for sheet_name, header_row in zip(file_specs['sheet_names'], file_specs['header_rows']):
            df = reader(
                file_path=file_path,
                sheet_name=sheet_name,
                header_row=header_row,
            )
            df = eliminate_empty_rows(df)
            data[sheet_name] = df.fillna('')

    @staticmethod
    def load_func(file_path, sheet_name, header_row, data, reader):
        """Load function for data."""
        df = reader(
            file_path=file_path,
            sheet_name=sheet_name,
            header_row=header_row,
        )
        df = eliminate_empty_rows(df)
        data[sheet_name] = df.fillna('')

    @staticmethod
    def get_reader_instance():
        """Get reader."""
        # Could be done differently
        return load_excel
