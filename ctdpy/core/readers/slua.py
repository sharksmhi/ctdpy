# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2021-04-15 16:47
@author: johannes
"""
import re

from ctdpy.core import utils
from ctdpy.core.readers.seabird import SeaBird
from ctdpy.core.readers.metadata import XLSXmeta


class SeaBirdSLUA(SeaBird):
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

    def _extract_filename_information(self, filename):
        """

        :param filename:
        :return:
        """
        # pattern = '{sensor_id:5s}_{sensor_serial_number:4s}_{visit_date:%Y%m%d}_{sample_time:%H%M}_{cntry:2d}_{shipc:2d}_{serno:4d}.cnv'
        dictionary = {}
        info_list = filename.split('_')
        dictionary['INSTRUMENT_SERIE'] = info_list[1]
        return dictionary

    def _get_pos_format(self, value, remove_char=None):
        remove_char = remove_char or ''
        if type(value) is str:
            value = value.replace(' ', '').replace(',', '.').replace(remove_char, '')
        else:
            print(f'WARNING! position value is not a string ({value})')
        return value

    def _convert_formats(self, meta_dict, filename=None):
        """
        :param meta_dict:
        :return:
        """
        meta_dict['SERNO'] = self._get_serno(meta_dict['SERNO'])
        meta_dict['LATIT'] = self._get_pos_format(meta_dict['LATIT'], remove_char='N')
        meta_dict['LONGI'] = self._get_pos_format(meta_dict['LONGI'], remove_char='E')
        meta_dict.setdefault('PROJ', 'COD')
        meta_dict.setdefault('ORDERER', 'HAV, SLUA')
        meta_dict.setdefault('SLABO', 'SLUA')
        meta_dict.setdefault('ALABO', 'SLUA')
        meta_dict.setdefault('POSYS', 'GPS')
        if filename:
            fid_info = self._extract_filename_information(filename)
            for item, value in fid_info.items():
                meta_dict[item] = value

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
        self._convert_formats(meta_dict, filename=filename)

        return meta_dict

    def get_meta_dict(self, series, keys=None, identifier='', separator=''):
        """
        :param series: pd.Series, contains metadata
        :param keys: List of keys to search for
        :param identifier: str
        :param separator: str
        :return: Dictionary
        """

        # Overwrites baseclass method

        meta_dict = {}
        boolean_startswith = self.get_index(series, identifier, as_boolean=True)
        if keys:
            for key in keys:
                boolean_contains = self.get_index(series, key, contains=True,
                                                  as_boolean=True)
                boolean = boolean_startswith & boolean_contains
                if any(boolean):
                    value = series[boolean].tolist()[0]

                    if separator in value:
                        meta = value.split(separator)[-1].strip()
                    else:
                        #FIXME do we really want this? better to SLAM down hard with a KeyError/ValueError?
                        meta = value[value.index(key)+len(key):].strip()

                    if ']' in meta:
                        # special SLUA fix. (** Latitude: [57 29.22 N] 57 29.22 N)
                        meta = meta.split(']')[1].strip()

                    if meta:
                        meta_dict.setdefault(key, meta)
        else:
            return series.loc[boolean_startswith]
        return meta_dict

    def _setup_dataframe(self, serie, metadata=None):
        """
        :param serie: pd.Series
        :return: pd.DataFrame
        """
        # print(self.df_handler.__dict__)
        header = self.get_data_header(serie, dataset='cnv')
        df = self.get_data_in_frame(serie, header, dataset='cnv')
        df = self.df_handler.map_column_names_of_dataframe(df)

        return df


class MetadataSLUA(XLSXmeta):
    """
    """
    def __init__(self, settings):
        super().__init__(settings)
        self.data = {}
        self.file_specs = self.settings.readers['slua']['datasets']['xlsx']
