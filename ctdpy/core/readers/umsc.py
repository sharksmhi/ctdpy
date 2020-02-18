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

import numpy as np
from ctdpy.core import utils
from ctdpy.core.data_handlers import DataFrameHandler
from ctdpy.core.readers.seabird import SeaBird
from ctdpy.core.readers.metadata import XLSXmeta
from ctdpy.core.calculator import Calculator


class SeaBirdUMSC(SeaBird):
    """
    """
    def __init__(self, settings):
        super().__init__(settings)

    @staticmethod
    def add_calculated_parameters(df, latit):
        """
        :param df:
        :param latit:
        :return:
        """
        calc = Calculator()
        df['DEPH'] = calc.get_true_depth(attribute_dictionary={'latitude': latit,
                                                               'pressure': df['PRES_CTD'].astype(np.float),
                                                               'gravity': df['PRES_CTD'].astype(np.float),
                                                               'density': df['DENS_CTD'].astype(np.float)})

    def _get_datetime(self, date_string):
        """
        Expecting date_string with format e.g. "Feb 21 2018 16:08:54 [Instrument's time stamp, header]"
        :param date_string: str
        :return:
        """
        if not date_string:
            return ''
        return utils.convert_string_to_datetime_obj(date_string.split('[')[0].strip(),
                                                    '%b %d %Y %H:%M:%S')

    def _convert_formats(self, meta_dict, filename):
        """
        :param meta_dict:
        :return:
        """
        timestamp = self._get_datetime(meta_dict['SDATE'])
        meta_dict['SDATE'] = utils.get_format_from_datetime_obj(timestamp, '%Y-%m-%d')
        meta_dict['STIME'] = utils.get_format_from_datetime_obj(timestamp, '%H:%M')
        # meta_dict['SERNO'] = self._get_serno(meta_dict['SERNO'])
        # meta_dict.setdefault('PROJ', 'BAS')
        # meta_dict.setdefault('ORDERER', 'HAV, SMHI')
        meta_dict.setdefault('SLABO', 'UMSC')
        meta_dict.setdefault('ALABO', 'UMSC')
        meta_dict.setdefault('POSYS', 'GPS')
        if filename:
            meta_dict['FILE_NAME'] = filename

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
            # meta_dict = {self.settings.pmap.get(key): meta_dict[key] for key in meta_dict}
            new_dict = {}
            for key in meta_dict:
                if meta_dict[key]:
                    new_dict.setdefault(self.settings.pmap.get(key), meta_dict[key])
            meta_dict = new_dict

        self._convert_formats(meta_dict, filename)

        return meta_dict

    def _setup_dataframe(self, serie, metadata):
        """
        :param serie:
        :param metadata:
        :return:
        """
        header = self.get_data_header(serie, dataset='cnv')
        df = self.get_data_in_frame(serie, header, dataset='cnv')
        df = self.df_handler.map_column_names_of_dataframe(df)

        self.add_calculated_parameters(df, latit=62.)  # metadata['LATIT'])

        return df


class MetadataUMSC(XLSXmeta):
    """
    """
    def __init__(self, settings):
        super().__init__(settings)
        self.data = {}
        self.file_specs = self.settings.readers['umsc']['datasets']['xlsx']
