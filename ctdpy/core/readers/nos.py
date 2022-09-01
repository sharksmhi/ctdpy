# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 09:37:38 2018

@author: a002028
"""
from ctdpy.core import utils
from ctdpy.core.readers.seabird import SeaBird
from ctdpy.core.readers.metadata import XLSXmeta


class SeaBirdNOS(SeaBird):
    """Reader for seabird data according to SMHI processing routines."""

    def __init__(self, settings):
        """Initialize."""
        super().__init__(settings)
        self._running_serno = 1

    def _extract_filename_information(self, filename):
        """Get filename information."""
        dictionary = {}
        info_list = filename.split('_')
        dictionary['INSTRUMENT_SERIE'] = info_list[1]
        return dictionary

    def _convert_formats(self, meta_dict, filename=None):
        """Set and/or convert formats of metadata."""
        meta_dict['SDATE'] = utils.get_format_from_datetime_obj(
            meta_dict['TIMESTAMP'], '%Y-%m-%d')
        meta_dict['STIME'] = utils.get_format_from_datetime_obj(
            meta_dict['TIMESTAMP'], '%H:%M')

        # meta_dict['SERNO'] = str(self._running_serno).zfill(4)
        meta_dict.setdefault('PROJ', 'NOS')
        meta_dict.setdefault('ORDERER', 'HAV')
        meta_dict.setdefault('SLABO', 'SMHI')
        meta_dict.setdefault('ALABO', 'SMHI')
        meta_dict.setdefault('POSYS', 'GPS')
        if filename:
            fid_info = self._extract_filename_information(filename)
            for item, value in fid_info.items():
                meta_dict[item] = value

    def get_metadata(self, serie, map_keys=True, filename=None):
        """Return dictionary with metadata."""
        meta_dict = {}
        for ident, sep in zip(['identifier_metadata', 'identifier_metadata_2'],
                              ['separator_metadata', 'separator_metadata_2']):
            data = self.get_meta_dict(
                serie,
                identifier=self.settings.datasets['cnv'].get(ident),
                separator=self.settings.datasets['cnv'].get(sep),
                keys=self.settings.datasets['cnv'].get('keys_metadata')
            )

            meta_dict = utils.recursive_dict_update(meta_dict, data)

        if map_keys:
            new_dict = {}
            for key in meta_dict:
                if meta_dict[key]:
                    new_dict.setdefault(self.settings.pmap.get(key),
                                        meta_dict[key])
            meta_dict = new_dict
        self._convert_formats(meta_dict, filename=filename)

        return meta_dict

    def get_meta_dict(self, series, keys=None, identifier='', separator=''):
        """Get metadata in dictionary.

        Args:
            series (pd.Series): Contains metadata
            keys (list): Keys to search for
            identifier (str): Used to identify metadata
            separator (str): Seperate string value into valuble metadata
        """
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
                        meta = value[value.index(key) + len(key):].strip()

                    if key == 'cast':
                        # Example str: '3 10 Oct 2015 08:31:43 samples 6673...'
                        meta_dict.setdefault(
                            'timestamp',
                            utils.get_timestamp(' '.join(value.split()[3:7]))
                        )
                    elif meta:
                        meta_dict.setdefault(key, meta)
        else:
            return series.loc[boolean_startswith]
        return meta_dict

    def _setup_dataframe(self, serie, metadata=None):
        """Convert pandas Serie into pandas DataFrame."""
        header = self.get_data_header(serie, dataset='cnv')
        df = self.get_data_in_frame(serie, header, dataset='cnv')
        df = self.df_handler.map_column_names_of_dataframe(df)

        return df


class MetadataNOS(XLSXmeta):
    """Reader for metadata according to SMHI datahost template."""

    def __init__(self, settings):
        """Initialize."""
        super().__init__(settings)
        self.data = {}
        self.file_specs = self.settings.readers['nos']['datasets']['xlsx']
