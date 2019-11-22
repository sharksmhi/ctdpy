# -*- coding: utf-8 -*-
"""
Created on 2019-11-21 12:27

@author: a002028

"""
import utils
import config
from core.data_handlers import SeriesHandler
from core.data_handlers import BaseReader
from core.readers.cnv_reader import CNVreader


class BaseSTDFMT(BaseReader, CNVreader, SeriesHandler):
    """
    """
    def __init__(self, settings):
        super().__init__(settings)

    def setup_dataframe(self, serie):
        """
        :param serie:
        :param metadata: used if needed for parameter calculations
        :return:
        """
        header = self.get_data_header(serie, dataset='txt', first_row=True)
        df = self.get_data_in_frame(serie, header, dataset='txt', splitter=True)
        self._adjust_dataframe(df)

        return df

    def setup_dictionary(self, fid, data, keys):
        """
        :param fid: str, file name identifier
        :return: standard dictionary structure
        """
        data[fid] = {key: None for key in keys}


class StandardFormatCTD(BaseSTDFMT):
    """
    """
    def __init__(self, settings):
        super().__init__(settings)

    def _adjust_dataframe(self, df):
        """
        :param df:
        :return:
        """
        if df.iloc[0, 0] == df.columns[0]:
            df.drop(0, inplace=True)
            df.reset_index(drop=True, inplace=True)

    def get_data(self, filenames=None, add_low_resolution_data=False):
        """
        :param filenames: list of file paths
        :return:
        """
        data = {}
        for fid in filenames:
            file_data = self.load(fid, sep='NO__SEPERATOR')
            fid = utils.get_filename(fid)
            self.setup_dictionary(fid, data, ('data', 'metadata'))

            serie = self.get_series_object(file_data)
            # print('serie', serie)
            metadata = self.get_metadata(serie, filename=fid)
            # print('metadata')
            # from pprint import pprint
            # pprint(metadata)
            dataframe = self.setup_dataframe(serie)
            # print('dataframe', dataframe)

            data[fid]['data'] = dataframe
            data[fid]['metadata'] = metadata
            # break

        return data

    def get_metadata(self, serie, map_keys=True, filename=None):
        """
        :param serie: pd.Series
        :param map_keys: False or True
        :return: Dictionary with metadata
        """
        # meta_dict = {}

        #TODO right now, data is a pd.Series, no seperation of metadata..
        # perhaps we want to access the delivery_note / metadata / sensorinfo / information?
        # In that case, we remake this method..
        data = self.get_meta_dict(serie,
                                  identifier=self.settings.datasets['txt'].get('identifier_meta'),
                                  # separator=self.settings.datasets['txt'].get('separator_metadata'),
                                  # keys=self.settings.datasets['txt'].get('keys_metadata'),
                                  )

        # meta_dict = config.recursive_dict_update(meta_dict, data)

        # if map_keys:
        #     meta_dict = {self.settings.pmap.get(key): meta_dict[key] for key in meta_dict}

        return data

