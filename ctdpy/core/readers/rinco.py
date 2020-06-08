# -*- coding: utf-8 -*-
"""
Created on 2019-12-11 15:28

@author: a002028

"""
""" Rinco reader
"""
import sys
sys.path.append("..")

import numpy as np

from ctdpy.core import utils
from ctdpy.core.data_handlers import DataFrameHandler
from ctdpy.core.data_handlers import SeriesHandler
from ctdpy.core.data_handlers import BaseReader
from ctdpy.core.readers.cnv_reader import CNVreader
from ctdpy.core.profile import Profile

from ctdpy.core.calculator import Calculator


class Rinco(BaseReader, CNVreader, SeriesHandler):
    """
    """
    ts_map = {'YEAR': 'year',
              'MONTH': 'month',
              'DAY': 'day',
              'HOUR': 'hour',
              'MINUTE': 'minute',
              'SECOND': 'second'}

    def __init__(self, settings):
        super().__init__(settings)
        self.df_handler = DataFrameHandler(self.settings)
        # self.metadata_update = {'Sensorinfo': {}}

    def add_calculated_parameters(self, df, latit):
        """
        :param df:
        :param latit:
        :return:
        """
        # if 'DEPH' not in df:
        #     calc = Calculator()
        #     df['DEPH'] = calc.get_true_depth(attribute_dictionary={'latitude': latit,
        #                                                            'pressure': df['PRES_CTD'].astype(np.float),
        #                                                            'gravity': df['PRES_CTD'].astype(np.float),
        #                                                            'density': df['DENS_CTD'].astype(np.float)})
            # self.metadata_update.setdefault('DEPH': )

        timestamp_array = df[['SDATE', 'STIME']].apply(lambda x: utils.get_timestamp(' '.join(x)), axis=1)
        for ts_key in self.ts_map:
            df[ts_key] = timestamp_array.dt.__getattribute__(self.ts_map.get(ts_key)).astype(str)
            df[ts_key] = df[ts_key].str.zfill(2)

    def get_data(self, filenames=None, add_low_resolution_data=False):
        """
        :param filenames: list of file paths
        :param merge_data_and_metadata: False or True
        :param add_low_resolution_data: False or True
        :return: datasets
        """
        data = {}
        if add_low_resolution_data:
            profile = Profile()

        for fid in filenames:
            file_data = self.load(fid)
            fid = utils.get_filename(fid)
            self.setup_dictionary(fid, data)

            serie = self.get_series_object(file_data)
            hires_data = self.setup_dataframe(serie, None)  #, metadata)
            metadata = self.get_metadata(serie, filename=fid,
                                         sdate=hires_data['SDATE'][0],
                                         stime=hires_data['STIME'][0])

            data[fid]['raw_format'] = serie
            data[fid]['metadata'] = metadata
            data[fid]['hires_data'] = hires_data
            data[fid]['identifier_data'] = self.settings.datasets['tob']['identifier_data']

            if add_low_resolution_data:
                profile.update_data(data=hires_data)
                lores_data = profile.extract_lores_data(key_depth='DEPH',
                                                        discrete_depths=self.settings.depths)
                data[fid]['lores_data'] = lores_data

        return data

    def get_metadata(self, serie, map_keys=True, filename=None):
        """
        :param serie: pd.Series
        :param map_keys: False or True
        :return: Dictionary with metadata
        """
        raise NotImplementedError

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

    def setup_dataframe(self, serie, metadata):
        """
        :param serie:
        :param metadata: used if needed for parameter calculations
        :return:
        """
        header = self.get_data_header(serie, dataset='tob', first_row=True)
        if header[0] == ';':
            header.remove(';')
        df = self.get_data_in_frame(serie, header, dataset='tob')
        df = self.df_handler.map_column_names_of_dataframe(df)

        self.add_calculated_parameters(df, latit=59.)  # metadata['LATIT'])

        return df

    def setup_dictionary(self, fid, data):
        """
        :param fid: str, file name identifier
        :return: standard dictionary structure
        """
        data[fid] = {'hires_data': None,
                     'lores_data': None,
                     'metadata': None}
