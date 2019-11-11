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
import numpy as np
from core.data_handlers import DataFrameHandler
from core.readers.seabird import SeaBird
from core.readers.metadata import XLSXmeta
from core.calculator import Calculator


class SeaBirdUMSC(SeaBird):
    """
    """
    def __init__(self, settings):
        super().__init__(settings)

    def add_calculated_parameters(self, df, latit):
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

    def _setup_dataframe(self, serie, metadata):
        """
        :param serie:
        :param metadata:
        :return:
        """
        header = self.get_data_header(serie, dataset='cnv')
        df = self.get_data_in_frame(serie, header, dataset='cnv')
        df = self.df_handler.map_column_names_of_dataframe(df)

        self.add_calculated_parameters(df, latit=62.) # metadata['LATIT'])

        return df


class MetadataUMSC(XLSXmeta):
    """
    """
    def __init__(self, settings):
        super().__init__(settings)
        self.data = {}
        self.file_specs = self.settings.readers['umsc']['datasets']['xlsx']
