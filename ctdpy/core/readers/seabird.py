# -*- coding: utf-8 -*-
"""
Created on 2019-11-04 10:31

@author: a002028

"""
import re
from ctdpy.core import utils
from ctdpy.core.data_handlers import DataFrameHandler
from ctdpy.core.data_handlers import SeriesHandler
from ctdpy.core.data_handlers import BaseReader
from ctdpy.core.readers.cnv_reader import CNVreader
from ctdpy.core.profile import Profile


class SeaBird(BaseReader, CNVreader, SeriesHandler):
    """Base for all seabird readers."""

    def __init__(self, settings):
        """Initialize."""
        super().__init__(settings)
        self.df_handler = DataFrameHandler(self.settings)

    def load_func(self, fid, dictionary):
        """Load function for data."""
        file_data = self.load(fid)
        fid = utils.get_filename(fid)
        self.setup_dictionary(fid, dictionary)

        serie = self.get_series_object(file_data)
        metadata = self.get_metadata(serie, filename=fid)
        hires_data = self.setup_dataframe(serie, metadata=metadata)

        dictionary[fid]['raw_format'] = serie
        dictionary[fid]['metadata'] = metadata
        dictionary[fid]['data'] = hires_data

    def get_data(self, filenames=None, add_low_resolution_data=False, thread_load=False):
        """Get data and metadata.

        Args:
            filenames (iterable): A sequence of files that will be used to load data from.
            add_low_resolution_data: False | True
            thread_load: False | True
        """
        data = {}
        for fid in filenames:
            print('loading: {}'.format(fid))
            if thread_load:
                # If we don´t have a process starting instantly after data load,
                # we might just aswell load with thread processes
                utils.thread_process(self.load_func, fid, data)
            else:
                self.load_func(fid, data)

        return data

    def get_metadata(self, serie, map_keys=True, filename=None):
        """Return dictionary with metadata."""
        meta_dict = {}
        for ident, sep in zip(['identifier_metadata', 'identifier_metadata_2'],
                              ['separator_metadata', 'separator_metadata_2']):
            data = self.get_meta_dict(serie,
                                      identifier=self.settings.datasets['cnv'].get(ident),
                                      separator=self.settings.datasets['cnv'].get(sep),
                                      keys=self.settings.datasets['cnv'].get('keys_metadata'))

            meta_dict = utils.recursive_dict_update(meta_dict, data)

        if map_keys:
            meta_dict = {self.settings.pmap.get(key): meta_dict[key] for key in meta_dict}

        return meta_dict

    def merge_data(self, data, resolution='lores_data'):
        """Merge data with metadata.

        Args:
            data (dict): Dictionary of specified dataset
            resolution (str): key for resolution
        """
        for fid in data:
            in_data = data[fid][resolution]
            in_data = self.df_handler.add_metadata_to_frame(in_data,
                                                            data[fid]['metadata'],
                                                            len_col=len(data[fid][resolution].index))
            data[fid][resolution + '_all'] = in_data

    def setup_dataframe(self, serie, metadata=None):
        """Convert pandas Serie into pandas DataFrame."""
        header = self.get_data_header(serie, dataset='cnv')
        df = self.get_data_in_frame(serie, header, dataset='cnv')
        df = self.df_handler.map_column_names_of_dataframe(df)

        return df

    def setup_dictionary(self, fid, data, keys=None):
        """Set standard dictionary structure."""
        keys = keys or ['data', 'lores_data', 'metadata']
        data[fid] = {key: None for key in keys}

    def _get_datetime(self, date_string):
        """Convert data date format to datetime object.

        Expecting date_string with format e.g. "Feb 21 2018 16:08:54 [Instrument's time stamp, header]"
        """
        if not date_string:
            return ''
        return utils.convert_string_to_datetime_obj(date_string.split('[')[0].strip(),
                                                    '%b %d %Y %H:%M:%S')

    @staticmethod
    def _get_serno(value):
        """Get serie number of profile/visit.

        In SMHI Seabird CTD-files there usually are specified information about "LIMS Job", which is the SMHI-internal
        key number YEAR-SHIP-SERNO. This method picks out the SERNO number.
        """
        lims_job_list = re.findall(r"[0-9]{4}", value)
        if len(lims_job_list):
            serno = lims_job_list[-1]
        else:
            serno = ''

        return serno
