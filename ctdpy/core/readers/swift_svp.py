"""
Created on 2021-04-19 10:55
@author: johannes
"""
""" Swift-SVP reader
"""
import pandas as pd
from ctdpy.core import utils
from ctdpy.core.data_handlers import DataFrameHandler
from ctdpy.core.data_handlers import SeriesHandler
from ctdpy.core.data_handlers import BaseReader
from ctdpy.core.readers.cnv_reader import CNVreader
from ctdpy.core.profile import Profile


class SwiftSVP(BaseReader, CNVreader, SeriesHandler):
    """
    """
    def __init__(self, settings):
        super().__init__(settings)
        self.df_handler = DataFrameHandler(self.settings)

        self.settings.datasets['vp2'].get('identifier_metadata')
        self.row_identifier = {
            self.settings.datasets['vp2'].get('identifier_metadata'): {
                'start': self.settings.datasets['vp2'].get('identifier_metadata'),
                'stop': self.settings.datasets['vp2'].get('identifier_header')
            },
            self.settings.datasets['vp2'].get('identifier_header'): {
                'start': self.settings.datasets['vp2'].get('identifier_header'),
                'stop': self.settings.datasets['vp2'].get('identifier_data')
            },
            self.settings.datasets['vp2'].get('identifier_data'): {
                'start': self.settings.datasets['vp2'].get('identifier_data'),
                'stop': None
            }
        }

    def _convert_formats(self, *args, **kwargs):
        raise NotImplementedError

    def _info_from_timestamp(self, df):
        if 'TIMESTAMP' in df:
            df['TIMESTAMP'] = df['TIMESTAMP'].apply(pd.Timestamp)
            df['YEAR'] = df['TIMESTAMP'].dt.strftime('%Y')
            df['MONTH'] = df['TIMESTAMP'].dt.strftime('%m')
            df['DAY'] = df['TIMESTAMP'].dt.strftime('%d')
            df['HOUR'] = df['TIMESTAMP'].dt.strftime('%H')
            df['MINUTE'] = df['TIMESTAMP'].dt.strftime('%M')
            df['SECOND'] = df['TIMESTAMP'].apply(utils.milliseconds)

    @staticmethod
    def load(fid):
        return pd.read_csv(
            fid,
            header=None
        )

    def load_func(self, fid, dictionary):
        file_data = self.load(fid)
        fid = utils.get_filename(fid)
        self.setup_dictionary(fid, dictionary)

        serie = self.get_series_object(file_data)
        metadata = self.get_metadata(serie)
        self._convert_formats(metadata, filename=fid)

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

        for fid in filenames:
            print('loading: {}'.format(fid))
            if thread_load:
                # If we don´t have a process starting instantly after data load,
                # we might just aswell load with thread processes
                utils.thread_process(self.load_func, fid, data)
            else:
                self.load_func(fid, data)

        return data

    def get_metadata(self, serie, map_keys=True, **kwargs):
        """
        :param serie: pd.Series
        :param map_keys: False or True
        :return: Dictionary with metadata
        """
        meta_dict = {}
        data = self.get_meta_dict(
            serie,
            identifier=self.settings.datasets['vp2'].get('identifier_metadata'),
            separator=self.settings.datasets['vp2'].get('separator_metadata'),
            keys=self.settings.datasets['vp2'].get('keys_metadata'),
        )

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
            in_data = self.df_handler.add_metadata_to_frame(
                in_data,
                data[fid]['metadata'],
                len_col=len(data[fid][resolution].index),
            )
            data[fid][resolution + '_all'] = in_data

    def setup_dataframe(self, serie, metadata=None):
        """
        :param serie:
        :param metadata: used if needed for parameter calculations
        :return:
        """
        header = self.get_data_header(serie, dataset='vp2')
        df = self.get_data_in_frame(serie, header, dataset='vp2')
        df = self.df_handler.map_column_names_of_dataframe(df)
        self._info_from_timestamp(df)

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

    def get_meta_dict(self, series, keys=None, identifier='', separator=''):
        """
        :param series: pd.Series, contains metadata
        :param keys: List of keys to search for
        :param identifier: str
        :param separator: str
        :return: Dictionary
        """
        meta_dict = {}
        boolean_startswith = self.get_index(
            series,
            (self.row_identifier[identifier]['start'], self.row_identifier[identifier]['stop']),
            between=True,
            as_boolean=True,
        )

        if keys:
            for key in keys:
                boolean_contains = self.get_index(series, key, contains=True, as_boolean=True)
                boolean = boolean_startswith & boolean_contains
                if any(boolean):
                    value = series[boolean].tolist()[0]

                    if separator in value:
                        meta = value.split(separator)[-1].strip()
                    else:
                        #FIXME do we really want this? better to SLAM down hard with a KeyError/ValueError?
                        meta = value[value.index(key)+len(key):].strip()

                    if meta:
                        meta_dict.setdefault(key, meta)
        else:
            return series.loc[boolean_startswith]
        return meta_dict

    def get_data_header(self, data, dataset=None, idx=0, first_row=False):
        """
        Get header from identifier in settings file.
        Assumes all values shall be taken from 'idx' after splitting
        :param data: pd.Series
        :param dataset: str
        :param idx: Default 0 due to Standard Seabird output
                    Example: '=' is the splitter in this specific case
                    # name 2 = t090C: Temperature [ITS-90, deg C]
                    head will then be 't090C: Temperature [ITS-90, deg C]'
        :return: list of column names (header)
        """
        identifier = self.settings.datasets[dataset]['identifier_header']
        boolean = self.get_index(
            data,
            (self.row_identifier[identifier]['start'], self.row_identifier[identifier]['stop']),
            between=True,
            as_boolean=True,
        )

        splitter = self.settings.datasets[dataset].get('separator_header')
        header = [head.split(splitter)[idx].strip() for head in data[boolean]]

        return header

    def get_data_in_frame(self, series, columns, dataset=None, **kwargs):
        """
        Get data from pd.Series. separates row values in series into columns within the
        DataFrame
        :param series: pd.Series, data
        :param columns: list, column names
        :param dataset: str, reader specific dataset. Determines how to handle data format
        :return: pd.DataFrame
        """
        identifier = self.settings.datasets[dataset]['identifier_data']
        boolean = self.get_index(
            series,
            (self.row_identifier[identifier]['start'], self.row_identifier[identifier]['stop']),
            between=True,
            as_boolean=True,
        )

        # We exclude the first 2 rows of the identified datablock, eg.
        # Date / Time\tDepth\tPressure........
        #           \tm\tdBar\tMs-1\tDe........
        index = series[boolean].index[2:]

        splitter = self.settings.datasets[dataset].get('separator_data')

        if splitter:
            df = pd.DataFrame(series[index].str.split(splitter).tolist(), columns=columns).fillna('')
        else:
            df = pd.DataFrame(series[index].str.split().tolist(), columns=columns).fillna('')

        return df
