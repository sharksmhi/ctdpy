# -*- coding: utf-8 -*-
"""
Created on 2019-11-21 12:27

@author: a002028

"""
from ctdpy.core import utils
from ctdpy.core.data_handlers import SeriesHandler, BaseReader
from ctdpy.core.readers.cnv_reader import CNVreader


class BaseSTDFMT(BaseReader, CNVreader, SeriesHandler):
    """
    """
    def __init__(self, settings):
        super().__init__(settings)

    def setup_dataframe(self, serie, metadata=None):
        """
        :param serie:
        :param metadata: used if needed for parameter calculations
        :return:
        """
        header = self.get_data_header(serie, dataset='txt', first_row=True)
        df = self.get_data_in_frame(serie, header, dataset='txt', splitter=True)
        self._adjust_dataframe(df)

        return df

    def setup_dictionary(self, fid, data, keys=None):
        """
        :param fid: str, file name identifier
        :return: standard dictionary structure
        """
        keys = keys or ['data', 'lores_data', 'metadata']
        data[fid] = {key: None for key in keys}

    def _adjust_dataframe(self, df):
        raise NotImplementedError


class StandardFormatCTD(BaseSTDFMT):
    """
    """
    def __init__(self, settings):
        super().__init__(settings)

    @staticmethod
    def _adjust_dataframe(df):
        """
        :param df:
        :return:
        """
        if df.iloc[0, 0] == df.columns[0]:
            df.drop(0, inplace=True)
            df.reset_index(drop=True, inplace=True)

    def get_data(self, filenames=None, add_low_resolution_data=False, thread_load=False):
        """
        :param thread_load:
        :param add_low_resolution_data:
        :param filenames: list of file paths
        :return:
        """
        data = {}
        for fid in filenames:
            print('reading file: {}'.format(fid))
            if thread_load:
                # If we don´t have a process starting instantly after data load,
                # we might just aswell load with thread processes
                utils.thread_process(self.load_func, fid, data)
            else:
                self.load_func(fid, data)

        return data

    def load_func(self, fid, dictionary):
        """
        :param fid:
        :param dictionary:
        :return:
        """
        file_data = self.load(fid, sep='NO__SEPERATOR')
        fid = utils.get_filename(fid)
        dictionary[fid] = {}

        serie = self.get_series_object(file_data)
        metadata = self.get_metadata(serie, filename=fid)
        dataframe = self.setup_dataframe(serie)

        dictionary[fid]['data'] = dataframe
        dictionary[fid]['metadata'] = metadata

    def get_metadata(self, serie, map_keys=True, filename=None):
        """
        :param serie: pd.Series
        :param map_keys: False or True
        :return: Dictionary with metadata
        """
        # meta_dict = {}
        data = self.get_meta_dict(serie,
                                  identifier=self.settings.datasets['txt'].get('identifier_meta'),
                                  # separator=self.settings.datasets['txt'].get('separator_metadata'),
                                  # keys=self.settings.datasets['txt'].get('keys_metadata'),
                                  )

        # meta_dict = config.recursive_dict_update(meta_dict, data)

        # if map_keys:
        #     meta_dict = {self.settings.pmap.get(key): meta_dict[key] for key in meta_dict}

        return data
