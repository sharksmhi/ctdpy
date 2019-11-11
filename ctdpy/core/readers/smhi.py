# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 09:37:38 2018

@author: a002028
"""
""" Sea-Bird reader
"""
import sys
sys.path.append("..")

import config
from core.readers.seabird import SeaBird
from core.readers.metadata import XLSXmeta


class SeaBirdSMHI(SeaBird):
    """
    """
    def __init__(self, settings):
        super().__init__(settings)

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

    def _setup_dataframe(self, serie):
        """
        :param serie: pd.Series
        :return: pd.DataFrame
        """
        print(self.df_handler.__dict__)
        header = self.get_data_header(serie, dataset='cnv')
        df = self.get_data_in_frame(serie, header, dataset='cnv')
        df = self.df_handler.map_column_names_of_dataframe(df)
        
        return df


class MetadataSMHI(XLSXmeta):
    """
    """
    def __init__(self, settings):
        super().__init__(settings)
        self.data = {}
        self.file_specs = self.settings.readers['smhi']['datasets']['xlsx']
