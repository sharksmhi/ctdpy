# Copyright (c) 2020 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2021-04-19 10:50
@author: johannes
"""
import pandas as pd
from ctdpy.core.readers.swift_svp import SwiftSVP
from ctdpy.core.readers.metadata import XLSXmeta
from ctdpy.core.utils import get_filename


class SvpSGUS(SwiftSVP):
    """Swift-SVP reader, using SwiftSVP as base."""

    def __init__(self, settings):
        """Initialize."""
        super().__init__(settings)

    def _convert_formats(self, meta_dict, filename=None):
        """Set and/or convert formats of metadata."""
        meta_dict.setdefault('PROJ', 'NMK')
        meta_dict.setdefault('ORDERER', 'HAV')
        meta_dict.setdefault('SLABO', 'SGUS')
        meta_dict.setdefault('ALABO', 'SGUS')
        meta_dict.setdefault('POSYS', 'GPS')
        if 'TIMESTAMP' in meta_dict:
            try:
                ts = pd.Timestamp(meta_dict['TIMESTAMP'])
                meta_dict.setdefault('SDATE', ts.strftime('%Y-%m-%d'))
                meta_dict.setdefault('STIME', ts.strftime('%H:%M:%S'))
            except:
                pass

        if filename:
            fid_info = self._extract_filename_information(filename)
            for item, value in fid_info.items():
                meta_dict[item] = value

    def _extract_filename_information(self, name):
        # TODO come on now, make it nicer...
        # Example filename: 'upp20_001_VL_71142_200918153154.vp2'
        info_list = name.split('_')
        return {
            'STATN': '_'.join((info_list[:2])),
            'SERNO': info_list[1].zfill(4),
            'INSTRUMENT_SERIE': info_list[3]
        }


class MetadataSGUS(XLSXmeta):
    """Reader for metadata according to SMHI datahost template."""

    def __init__(self, settings):
        """Initialize. """
        super().__init__(settings)
        self.data = {}
        self.file_specs = self.settings.readers['sgus']['datasets']['xlsx']

    def get_data(self, filenames=None, add_low_resolution_data=False):
        """Get data and metadata.

        Args:
            filenames (iterable): A sequence of files that will be used to load data from.
            add_low_resolution_data: False | True
        """
        data = {}
        reader = self.get_reader_instance()
        for file_path in filenames:
            fid = get_filename(file_path)
            data[fid] = {}
            self._read(file_path, self.file_specs, reader, data[fid])

            if 'Metadata' in data[fid]:
                data[fid]['Metadata'] = self._add_serno(data[fid]['Metadata'])

        return data

    def _add_serno(self, df):
        """Add serno to dataframe."""
        if set(df['SERNO']) == {''}:
            # df['SERNO'] = df['FILE_NAME'].apply(lambda x: x.split('_')[1].zfill(4))
            df = df.sort_values(
                ['SDATE', 'STIME'],  ascending=[True, True]
            ).reset_index(drop=True)
            df['SERNO'] = (df.index + 1).map(str).str.zfill(4)

        return df