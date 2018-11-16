# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 11:01:38 2018

@author: a002028
"""
#
#
""" Sea-Bird-UMSC reader 
"""
import sys

sys.path.append("..")
import config
from core.data_handlers import DataFrameHandler
from core.data_handlers import SeriesHandler
from core.data_handlers import BaseReader
from core.readers.cnv_reader import CNVreader
from core import ctd_profile

"""
#==============================================================================
#==============================================================================
"""


class SeaBirdUMSC(BaseReader, CNVreader, SeriesHandler):
    """
    """

    def __init__(self, settings):
        super().__init__(settings)
        self.data_dict = {}
        self.df_handler = DataFrameHandler(self.settings)

    def get_data(self, filenames=None, merge_data_and_metadata=False):
        """

        :param filenames: list of file paths
        :param merge_data_and_metadata: False or True
        :return: datasets
        #TODO optional extraction of low resolution data
        """
        for fid in filenames:
            self._setup_dictionary(fid)

            data = self.load(fid)
            serie = self.get_series_object(data)

            hires_data = self._setup_dataframe(serie)
            profile = ctd_profile.CtdProfile(data=hires_data)
            lores_data = profile.extract_lores_data(key_depth='DEPH',
                                                    discrete_depths=self.settings.depths)

            self.data_dict[fid]['metadata'] = self.get_metadata(serie)
            self.data_dict[fid]['hires_data'] = hires_data
            self.data_dict[fid]['lores_data'] = lores_data

        return self.data_dict

    def get_metadata(self, serie, map_keys=True):
        """
        :param serie: pd.Series
        :param map_keys: False or True
        :return: Dictionary with metadata
        """
        meta_dict = {}
        for ident, sep in zip(['identifier_metadata', 'identifier_metadata_2'],
                              ['separator_metadata', 'separator_metadata_2']):
            data = self.get_meta_dict(serie,
                                      identifier=self.settings.datasets['cnv'].get(ident),
                                      separator=self.settings.datasets['cnv'].get(sep),
                                      keys=self.settings.datasets['cnv'].get('keys_metadata'))

            meta_dict = config.recursive_dict_update(meta_dict, data)

        if map_keys:
            meta_dict = {self.settings.pmap.get(key): meta_dict[key] for key in meta_dict}

        return meta_dict

    def merge_data(self, data, resolution='lores_data'):
        """
        :param data: Dictionary of specified dataset
        :param resolution: str
        :return: data with added metadata
        """
        for fid in data:
            in_data = data[fid][resolution]
            in_data = self.df_handler.add_metadata_to_frame(in_data,
                                                            data[fid]['metadata'],
                                                            len_col=len(data[fid][resolution].index))
            data[fid][resolution + '_all'] = in_data

        return data

    def _setup_dataframe(self, serie):
        """
        :param serie: pd.Series
        :return: pd.DataFrame
        """
        header = self.get_data_header(serie, dataset='cnv')
        df = self.get_data_in_frame(serie, header, dataset='cnv')
        df = self.df_handler.map_column_names_of_DataFrame(df)

        return df

    def _setup_dictionary(self, fid):
        """
        :param fid: str, file name identifier
        :return: standard dictionary structure
        """
        self.data_dict[fid] = {'hires_data': None,
                               'lores_data': None,
                               'metadata': None}
