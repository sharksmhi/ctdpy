# -*- coding: utf-8 -*-
"""
Created on 2019-11-04 10:31

@author: a002028

"""
""" Sea-Bird reader
"""
from ctdpy.core import utils
from ctdpy.core.data_handlers import DataFrameHandler
from ctdpy.core.data_handlers import SeriesHandler
from ctdpy.core.data_handlers import BaseReader
from ctdpy.core.readers.cnv_reader import CNVreader
from ctdpy.core.profile import Profile


class SeaBird(BaseReader, CNVreader, SeriesHandler):
    """
    """
    def __init__(self, settings):
        super().__init__(settings)
        self.df_handler = DataFrameHandler(self.settings)

    def load_func(self, fid, dictionary):
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
        """
        :param thread_load: does not seem to be working as expected.. yes it´s done in 1 sec but the loading function
        are busy for 30 sec..
        :param filenames: list of file paths
        :param add_low_resolution_data: False or True
        :return: datasets
        """
        data = {}
        profile = None
        if add_low_resolution_data:
            profile = Profile()
        print('thread_load', thread_load)
        for fid in filenames:
            print('loading: {}'.format(fid))
            if thread_load:
                # If we don´t have a process starting instantly after data load,
                # we might just aswell load with thread processes
                utils.thread_process(self.load_func, fid, data)
            else:
                self.load_func(fid, data)

            # file_data = self.load(fid)
            # fid = utils.get_filename(fid)
            # self.setup_dictionary(fid, data, None)
            #
            # serie = self.get_series_object(file_data)
            # metadata = self.get_metadata(serie, filename=fid)
            # hires_data = self.setup_dataframe(serie, metadata)
            #
            # data[fid]['raw_format'] = serie
            # data[fid]['metadata'] = metadata
            # data[fid]['data'] = hires_data

            # if add_low_resolution_data:
            #     profile.update_data(data=hires_data)
            #     lores_data = profile.extract_lores_data(key_depth='DEPH',
            #                                             discrete_depths=self.settings.depths)
            #     data[fid]['lores_data'] = lores_data
        print('return data')
        return data

    def get_metadata(self, serie, map_keys=True, filename=None):
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

            meta_dict = utils.recursive_dict_update(meta_dict, data)

        if map_keys:
            meta_dict = {self.settings.pmap.get(key): meta_dict[key] for key in meta_dict}

        return meta_dict

    def merge_data(self, data, resolution='lores_data'):
        """
        :param data: Dictionary of specified dataset
        :param resolution: str
        :return: Updates data (dictionary with pd.DataFrames)
        """
        for fid in data:
            in_data = data[fid][resolution]
            in_data = self.df_handler.add_metadata_to_frame(in_data,
                                                            data[fid]['metadata'],
                                                            len_col=len(data[fid][resolution].index))
            data[fid][resolution + '_all'] = in_data

    def setup_dataframe(self, serie, metadata=None):
        """
        :param serie:
        :param metadata: used if needed for parameter calculations
        :return:
        """
        header = self.get_data_header(serie, dataset='cnv')
        df = self.get_data_in_frame(serie, header, dataset='cnv')
        df = self.df_handler.map_column_names_of_dataframe(df)

        return df

    def setup_dictionary(self, fid, data, keys=None):
        """
        :param keys:
        :param data:
        :param fid: str, file name identifier
        :return: standard dictionary structure
        """
        keys = keys or ['data', 'lores_data', 'metadata']
        data[fid] = {key: None for key in keys}
