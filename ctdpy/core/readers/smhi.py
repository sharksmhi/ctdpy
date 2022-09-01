# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 09:37:38 2018

@author: a002028
"""
from ctdpy.core import utils
from ctdpy.core.readers.seabird import SeaBird
from ctdpy.core.readers.metadata import XLSXmeta, TXTmeta


class SeaBirdSMHI(SeaBird):
    """Reader for seabird data according to SMHI processing routines."""

    def __init__(self, settings):
        """Initialize."""
        super().__init__(settings)

    def _extract_filename_information(self, filename):
        """Get filename information."""
        dictionary = {}
        info_list = filename.split('_')
        dictionary['INSTRUMENT_SERIE'] = info_list[1]
        return dictionary

    def _convert_formats(self, meta_dict, filename=None):
        """Set and/or convert formats of metadata."""
        timestamp = self._get_datetime(meta_dict['SDATE'])
        meta_dict['SDATE'] = utils.get_format_from_datetime_obj(
            timestamp, '%Y-%m-%d')
        meta_dict['STIME'] = utils.get_format_from_datetime_obj(
            timestamp, '%H:%M')

        meta_dict['SERNO'] = self._get_serno(meta_dict['SERNO'])
        meta_dict.setdefault('PROJ', 'BAS')
        meta_dict.setdefault('ORDERER', 'HAV, SMHI')
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
                    new_dict.setdefault(
                        self.settings.pmap.get(key), meta_dict[key]
                    )
            meta_dict = new_dict
        self._convert_formats(meta_dict, filename=filename)

        return meta_dict

    def _setup_dataframe(self, serie, metadata=None):
        """Convert pandas Serie into pandas DataFrame."""
        header = self.get_data_header(serie, dataset='cnv')
        df = self.get_data_in_frame(serie, header, dataset='cnv')
        df = self.df_handler.map_column_names_of_dataframe(df)

        return df


class MVPSMHI(SeaBird):
    """Reader for MVP-data according to SMHI processing routines."""

    def __init__(self, settings):
        """Initialize."""
        super().__init__(settings)

    def _convert_formats(self, meta_dict):
        """Set and/or convert formats of metadata."""
        # meta_dict['SERNO'] = self._get_serno(meta_dict['SERNO'])
        meta_dict.setdefault('PROJ', 'BAS')
        meta_dict.setdefault('ORDERER', 'SMHI')
        meta_dict.setdefault('SLABO', 'SMHI')
        meta_dict.setdefault('ALABO', 'SMHI')
        meta_dict.setdefault('POSYS', 'GPS')

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
                    new_dict.setdefault(
                        self.settings.pmap.get(key), meta_dict[key]
                    )
            meta_dict = new_dict
        self._convert_formats(meta_dict)

        return meta_dict

    def _setup_dataframe(self, serie, metadata=None):
        """Convert pandas Serie into pandas DataFrame."""
        header = self.get_data_header(serie, dataset='cnv')
        df = self.get_data_in_frame(serie, header, dataset='cnv')
        df = self.df_handler.map_column_names_of_dataframe(df)

        return df


class MetadataSMHI(XLSXmeta):
    """Reader for metadata according to SMHI datahost template."""

    def __init__(self, settings):
        """Initialize."""
        super().__init__(settings)
        self.data = {}
        self.file_specs = self.settings.readers['smhi']['datasets']['xlsx']


class MetadataTxtSMHI(TXTmeta):
    """Text reader for metadata according to SMHI datahost template."""

    def __init__(self, settings):
        """Initialize."""
        super().__init__(settings)
        self.data = {}
        self.file_specs = self.settings.readers['smhi']['datasets']['txt']


class MasterSMHI(SeaBird):
    """Reader for seabird data according to the new SMHI processing routines."""

    def __init__(self, settings):
        """Initialize."""
        super().__init__(settings)

    def _extract_filename_information(self, filename):
        """Get filename information."""
        dictionary = {}
        info_list = filename.split('_')
        dictionary['INSTRUMENT_SERIE'] = info_list[1]
        dictionary['SERNO'] = info_list[-1].split('.')[0]
        return dictionary

    def _convert_formats(self, meta_dict, filename=None):
        """Set and/or convert formats of metadata."""
        timestamp = self._get_datetime(meta_dict['SDATE'])
        meta_dict['SDATE'] = utils.get_format_from_datetime_obj(
            timestamp, '%Y-%m-%d')
        meta_dict['STIME'] = utils.get_format_from_datetime_obj(
            timestamp, '%H:%M')

        # meta_dict['SERNO'] = self._get_serno(meta_dict['SERNO'])
        meta_dict.setdefault('PROJ', 'BAS')
        meta_dict.setdefault('ORDERER', 'HAV, SMHI')
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
                    new_dict.setdefault(
                        self.settings.pmap.get(key), meta_dict[key]
                    )
            meta_dict = new_dict
        self._convert_formats(meta_dict, filename=filename)

        return meta_dict

    def _setup_dataframe(self, serie, metadata):
        """Convert pandas Serie into pandas DataFrame."""
        header = self.get_data_header(serie, dataset='cnv')
        df = self.get_data_in_frame(serie, header, dataset='cnv')
        df = self.df_handler.map_column_names_of_dataframe(df)

        return df
