# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 09:37:38 2018

@author: a002028
"""
""" Sea-Bird reader
"""
import sys
sys.path.append("..")
import re

from ctdpy.core import utils
from ctdpy.core.readers.seabird import SeaBird
from ctdpy.core.readers.metadata import XLSXmeta


class SeaBirdSMHI(SeaBird):
    """
    """
    def __init__(self, settings):
        super().__init__(settings)

    @staticmethod
    def _get_serno(value):
        """
        IN SMHI Seabird CTD-files there usually are specified information about "LIMS Job", which is the SMHI-internal
        key number YEAR-SHIP-SERNO. This method picks out the SERNO number.
        :param value:
        :return:
        """
        lims_job_list = re.findall(r"[0-9]{4}", value)
        if len(lims_job_list):
            serno = lims_job_list[-1]
        else:
            serno = ''

        return serno

    def _convert_formats(self, meta_dict):
        """
        :param meta_dict:
        :return:
        """
        meta_dict['SERNO'] = self._get_serno(meta_dict['SERNO'])
        meta_dict.setdefault('PROJ', 'BAS')
        meta_dict.setdefault('ORDERER', 'HAV, SMHI')
        meta_dict.setdefault('SLABO', 'SMHI')
        meta_dict.setdefault('ALABO', 'SMHI')
        meta_dict.setdefault('POSYS', 'GPS')

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
        self._convert_formats(meta_dict)

        return meta_dict

    def _setup_dataframe(self, serie, metadata):
        """
        :param serie: pd.Series
        :return: pd.DataFrame
        """
        # print(self.df_handler.__dict__)
        header = self.get_data_header(serie, dataset='cnv')
        df = self.get_data_in_frame(serie, header, dataset='cnv')
        df = self.df_handler.map_column_names_of_dataframe(df)
        
        return df


class MVPSMHI(SeaBird):
    """
    """
    def __init__(self, settings):
        super().__init__(settings)

    @staticmethod
    def _get_serno(value):
        """
        IN SMHI Seabird CTD-files there usually are specified information about "LIMS Job", which is the SMHI-internal
        key number YEAR-SHIP-SERNO. This method picks out the SERNO number.
        :param value:
        :return:
        """
        lims_job_list = re.findall(r"[0-9]{4}", value)
        if len(lims_job_list):
            serno = lims_job_list[-1]
        else:
            serno = ''

        return serno

    def _convert_formats(self, meta_dict):
        """
        :param meta_dict:
        :return:
        """
        # meta_dict['SERNO'] = self._get_serno(meta_dict['SERNO'])
        meta_dict.setdefault('PROJ', 'BAS')
        meta_dict.setdefault('ORDERER', 'SMHI')
        meta_dict.setdefault('SLABO', 'SMHI')
        meta_dict.setdefault('ALABO', 'SMHI')
        meta_dict.setdefault('POSYS', 'GPS')

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
        self._convert_formats(meta_dict)

        return meta_dict

    def _setup_dataframe(self, serie, metadata):
        """
        :param serie: pd.Series
        :return: pd.DataFrame
        """
        # print(self.df_handler.__dict__)
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
