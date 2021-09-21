# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 11:01:38 2018

@author: a002028
"""
import re
import numpy as np
from ctdpy.core import utils
from ctdpy.core.readers.seabird import SeaBird
from ctdpy.core.readers.metadata import XLSXmeta
from ctdpy.core.calculator import Calculator


class SeaBirdUMSC(SeaBird):
    """Reader for seabird data according to UMSC processing routines."""

    def __init__(self, settings):
        """Initialize."""
        super().__init__(settings)

    @staticmethod
    def add_calculated_parameters(df, latit):
        """Add caluculated parameters to dataframe."""
        calc = Calculator()
        df['DEPH'] = calc.get_true_depth(attribute_dictionary={'latitude': latit,
                                                               'pressure': df['PRES_CTD'].astype(np.float),
                                                               'gravity': df['PRES_CTD'].astype(np.float),
                                                               'density': df['DENS_CTD'].astype(np.float)})

    def _convert_formats(self, meta_dict, filename):
        """Set and/or convert formats of metadata."""
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
        """Return dictionary with metadata."""
        meta_dict = {}
        for ident, sep in zip(['identifier_metadata', 'identifier_metadata_2'],
                              ['separator_metadata', 'separator_metadata_2']):
            data = self.get_meta_dict(serie,
                                      identifier=self.settings.datasets['cnv'].get(ident),
                                      separator=self.settings.datasets['cnv'].get(sep),
                                      keys=self.settings.datasets['cnv'].get('keys_metadata'))

            meta_dict = utils.recursive_dict_update(meta_dict, data)

        if map_keys:
            new_dict = {}
            for key in meta_dict:
                if meta_dict[key]:
                    new_dict.setdefault(self.settings.pmap.get(key), meta_dict[key])
            meta_dict = new_dict

        self._convert_formats(meta_dict, filename)

        return meta_dict

    def get_meta_dict(self, series, keys=None, identifier='', separator=''):
        """Get metadata information for a specific identifier and separator."""
        keys = keys or []
        meta_dict = {}
        boolean_startswith = self.get_index(series, identifier, as_boolean=True)
        if any(keys):
            for key in keys:
                boolean_contains = self.get_index(series, key, contains=True,
                                                  as_boolean=True)
                boolean = boolean_startswith & boolean_contains
                if any(boolean):
                    if key == 'SERIAL NO':
                        meta = re.search('SERIAL NO. (.+?) ', series[boolean].iloc[0]).group(1)
                    else:
                        meta = series[boolean].tolist()[0].split(separator)[-1].strip()
                    meta_dict.setdefault(key, meta)
        else:
            return series.loc[boolean_startswith]
        return meta_dict

    def _setup_dataframe(self, serie, metadata=None):
        """Convert pandas Serie into pandas DataFrame."""
        header = self.get_data_header(serie, dataset='cnv')
        df = self.get_data_in_frame(serie, header, dataset='cnv')
        df = self.df_handler.map_column_names_of_dataframe(df)

        # TODO use metadata['LATIT'] instead of 62.
        self.add_calculated_parameters(df, latit=62.)  # metadata['LATIT'])

        return df


class MetadataUMSC(XLSXmeta):
    """Metadata Class for UMSC reader."""

    def __init__(self, settings):
        """Initialize."""
        super().__init__(settings)
        self.data = {}
        self.file_specs = self.settings.readers['umsc']['datasets']['xlsx']
