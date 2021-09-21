# -*- coding: utf-8 -*-
"""
Created on 2019-12-11 15:26

@author: a002028

"""
from ctdpy.core import utils
from ctdpy.core.readers.rinco import Rinco
from ctdpy.core.readers.metadata import XLSXmeta


class RincoDEEP(Rinco):
    """Reader for rinco data according to DEEP processing routines."""

    def __init__(self, settings):
        """Initialize."""
        super().__init__(settings)

    def _get_statn(self, file_name, sdate):
        """Return station name in capital letters.

        DEEP CTD-data files follow pattern: {STATN}{SDATE}{~FILE_VERSION}{.TOB}
        where FILE_VERSION isn't always present.
        Example:
        file_name = 'B1180814.TOB'
        sdate = '180814'
        We find index for sdate string and extract station name.
        """
        sdate = utils.get_timestamp(sdate)
        date_str = utils.get_format_from_datetime_obj(sdate, '%y%m%d')
        try:
            index = self._get_string_index(file_name, date_str)
        except Exception:
            # The filename SDATE is based on when the ship arrived to the sampling station. Quite often the CTD-cast is
            # taken several hours later.. Which in turn means that SDATE can differ by one day between the
            # Station VISIT date and the SAMPLING date
            sdate = utils.get_timestamp_minus_daydelta(sdate, delta=1)
            date_str = utils.get_format_from_datetime_obj(sdate, '%y%m%d')
            index = self._get_string_index(file_name, date_str)

        statn = file_name[:index]
        return statn.upper()

    def _get_instrument_serie(self, serie):
        """Return instrument serial number.

        DEEP CTD-data files processing routines follow pattern '001 {INSTRUMENT_ID{INSTRUMENT_SERIE}}.... '
        We therefore locate rows that starts with '001 '..
        Example:
            StandardDataAcquisition SDA (C)opyright by T. Finger 1999-2010

            001 CTM469 001  N  Vbatt  Volt -1.5701 ...
            001 CTM469 002  P  Press  dbar -2.6940 ...
        """
        try:
            index = self.get_index(serie, '001 ')
            index = index[0]
            instrument_id = self._get_instrument_id(serie.iloc[index])
            instrument_serie = instrument_id.strip('CTM')
        except Exception:
            instrument_serie = None

        return instrument_serie

    @staticmethod
    def _get_instrument_id(string):
        """Return instrument ID."""
        for s in string.split():
            if s.startswith('CTM'):
                return s
        return None

    def _get_string_index(self, string, value):
        """Return index in a string where "value" is present."""
        return string.index(value)

    def _get_timestamp(self, sdate, stime):
        """Get pandas.TimeStamp of "sdate" and "stime"."""
        return utils.get_timestamp(' '.join((sdate, stime)))

    def _convert_formats(self, meta_dict):
        """Set and/or convert formats of metadata."""
        meta_dict['timestamp'] = self._get_timestamp(meta_dict['SDATE'], meta_dict['STIME'])
        statn = self._get_statn(meta_dict['FILE_NAME'], meta_dict['SDATE'])
        meta_dict.setdefault('STATN', statn)
        meta_dict.setdefault('SHIPC', '7798')
        meta_dict.setdefault('PROJ', 'BAS')
        meta_dict.setdefault('ORDERER', 'HAV')
        meta_dict.setdefault('SLABO', 'DEEP')
        meta_dict.setdefault('ALABO', 'DEEP')
        meta_dict.setdefault('POSYS', 'NOM')

    def get_metadata(self, serie, map_keys=True, filename=None, sdate=None, stime=None):
        """Return dictionary with metadata."""
        instrument_serie = self._get_instrument_serie(serie)
        meta_dict = {'FILE_NAME': filename,
                     'SDATE': sdate,
                     'STIME': stime,
                     'INSTRUMENT_SERIE': instrument_serie
                     }
        if map_keys:
            new_dict = {}
            for key in meta_dict:
                if meta_dict[key]:
                    new_dict.setdefault(self.settings.pmap.get(key), meta_dict[key])
            meta_dict = new_dict
        self._convert_formats(meta_dict)

        return meta_dict

    def _setup_dataframe(self, serie, metadata=None):
        """Convert pandas Serie into pandas DataFrame."""
        header = self.get_data_header(serie, dataset='tob')
        df = self.get_data_in_frame(serie, header, dataset='tob')
        df = self.df_handler.map_column_names_of_dataframe(df)

        return df


class MetadataDEEP(XLSXmeta):
    """Reader for metadata according to SMHI datahost template."""

    def __init__(self, settings):
        """Initialize."""
        super().__init__(settings)
        self.data = {}
        self.file_specs = self.settings.readers['deep']['datasets']['xlsx']
