# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 13:26:05 2018

@author: a002028
"""
import pandas as pd
import numpy as np
import seawater
from ctdpy.core.readers.file_handlers import BaseFileHandler
from ctdpy.core.readers.txt_reader import load_txt
from ctdpy.core import utils
import warnings
warnings.filterwarnings("ignore", 'This pattern has match groups')


class DataFrameHandler(BaseFileHandler):
    """Handler for dataframes."""

    # TODO perhaps we should move staticmethods (.get_"datetimes", _"position" to utils?

    def __init__(self, settings):
        """Store the settings object."""
        super().__init__(settings)
        self.settings = settings

    def map_column_names_of_dataframe(self, df):
        """Map column names of the given dataframe."""
        map_dict = self.settings.pmap.get_parameter_mapping(df.columns.tolist())
        return self._rename_columns_of_dataframe(df, map_dict)

    @staticmethod
    def _rename_columns_of_dataframe(df, mapping_dict):
        """Return dataframe with renamed columns.

        Args:
            df: pandas.DataFrame
            mapping_dict: dictionary with old names as keys and new names as values.

        """
        return df.rename(index=str, columns=mapping_dict)

    @staticmethod
    def add_metadata_to_frame(df, meta, len_col=None):
        """Return a merged dataframe.

        Args:
            df: pandas.DataFrame
            meta: Dictionary with metadata
            len_col: Length of DataFrame columns
        """
        df_meta = pd.DataFrame({k: [meta[k]] * len_col for k in meta})
        df = df.reset_index(drop=False)  # orginal index of df is saved
        df = pd.concat([df, df_meta], axis=1)
        return df

    @staticmethod
    def get_data_header(df, *args, **kwargs):
        """Return header of data. Base method meant to be overwriten."""
        return df.columns

    @staticmethod
    def get_index(data, key, string):
        """Get index of string value of pandas Serie."""
        # TODO Ever used? do we only use SeriesHandler.get_index() ??
        # FIXME use pandas isin instead.. booleans..
        return np.where(data[key] == string)[0]

    @staticmethod
    def get_datetime_format(df, sdate_key=None, stime_key=None):
        """Get datetime array. Uses date and time to create array with datetime object."""
        datetime_format = np.vectorize(utils.get_datetime)(df[sdate_key], df[stime_key])
        return datetime_format

    @staticmethod
    def get_sdate(datetime_obj, fmt='%Y-%m-%d'):
        """Return date string array according to fmt from datatime array."""
        stime = np.vectorize(utils.get_format_from_datetime_obj)(datetime_obj, fmt)
        return stime

    @staticmethod
    def get_stime(datetime_obj, fmt='%H:%M:%S'):
        """Return time string array according to fmt from datatime array."""
        stime = np.vectorize(utils.get_format_from_datetime_obj)(datetime_obj, fmt)
        return stime

    @staticmethod
    def get_position_decimal_degrees(pos_serie):
        """Return array of positions according to format DD.dddd.

        Uses numpy.vectorize to transform position format DDMM.mm into DD.dddd

        Args: pos_serie pos_serie: pd.Series of coordinates in format DDMM.mm
        """
        pos = np.vectorize(utils.decmin_to_decdeg)(pos_serie)
        return pos

    @staticmethod
    def reset_index(df):
        """Reset the index array for the given dataframe."""
        df.reset_index(inplace=True, drop=True)


class SeriesHandler(BaseFileHandler):
    """Handles pandas.Series."""

    def __init__(self, settings):
        """Store the settings object."""
        super().__init__(settings)
        self.settings = settings

    def update_datetime_object(self, date_string, time_string):
        """Set time information properties.

        See the different setters of year, month day, hour, minute, second under the class BaseFileHandler.
        """
        datetime_obj = utils.get_datetime(date_string, time_string)
        self.year = datetime_obj
        self.month = datetime_obj
        self.day = datetime_obj
        self.hour = datetime_obj
        self.minute = datetime_obj
        self.second = datetime_obj

    def update_position(self, lat, lon):
        """Set position information properties.

        See the different setters of latitude_dd, longitude_dd under the class BaseFileHandler.
        """
        self.latitude_dd = lat
        self.longitude_dd = lon

    def update_cruise(self, shipc, cruise_no):
        """Set cruise information properties.

        See setter of cruise under the class BaseFileHandler.
        Specific cruise number, YYYY_SHIP_NNNN. Should be updated?
        """
        if cruise_no:
            self.cruise = [self.year, shipc, cruise_no]
        else:
            self.cruise = ''

    def update_station_name(self, statn):
        """Set station information properties.

        See setter of station under the class BaseFileHandler.
        Station name at visit.
        """
        self.station = statn

    def get_data_header(self, data, dataset=None, idx=1, first_row=False):
        """Get header from identifier in settings file.

        Assumes all values shall be taken from string 'idx' after splitting
        Args:
            data (pandas.Series): Data to get header information from.
            dataset (string): Key of setting dataset.
            idx: Default 1 due to Standard Seabird output
                 Example: '=' is the splitter in this specific case
                 # name 2 = t090C: Temperature [ITS-90, deg C]
                 head will then be 't090C: Temperature [ITS-90, deg C]'
        """
        identifier_header = self.settings.datasets[dataset]['identifier_header']
        reversed = '~' in identifier_header
        index = self.get_index(data, identifier_header.replace('~', ''), reversed_boolean=reversed)
        splitter = self.settings.datasets[dataset].get('separator_header')
        if first_row:
            if not splitter or splitter == 'None':
                header = data[index].iloc[0].split()
            else:
                header = data[index].iloc[0].split(splitter)
        else:
            header = [head.split(splitter)[idx].strip() for head in data[index]]

        header = self.map_doublet_columns(header)

        return header

    @staticmethod
    def map_doublet_columns(header):
        """Get header including doublet columns."""
        # Fixme Do we need to rewrite this method to include x number of doublets instead of just 2?
        doublet_dict = {col: header.count(col) for col in header}
        new_header = []
        for col in header:
            if doublet_dict.get(col) > 1 and col in new_header:
                # Assuming we only have two columns of the same name
                new_header.append(col + '_2')
            else:
                new_header.append(col)
        return new_header

    def get_data_in_frame(self, series, columns, dataset=None, splitter=None):
        """Get data from pd.Series into a pd.DataFrame. Separates row values into columns.

        Args:
            series (pd.Series): Data
            columns (list): Column names
            dataset (str): Reader specific dataset.
                           Determines how to handle data format.
        """
        # FIXME NO! not the way to go! if anything, add reversed as input argument! let the identifier be clean!
        identifier_header = self.settings.datasets[dataset]['identifier_data']
        reversed = '~' in identifier_header
        idx = self.get_index(series, identifier_header.replace('~', ''), reversed_boolean=reversed)
        if splitter:
            splitter = self.settings.datasets[dataset]['separator_data']
            df = pd.DataFrame(series[idx].str.split(splitter).tolist(), columns=columns).fillna('')
        else:
            df = pd.DataFrame(series[idx].str.split().tolist(), columns=columns).fillna('')
        return df

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
                        # FIXME do we really want this? better to SLAM down hard with a KeyError/ValueError?
                        meta = value[value.index(key) + len(key):].strip()

                    if meta:
                        meta_dict.setdefault(key, meta)
        else:
            return series.loc[boolean_startswith]
        return meta_dict

    @staticmethod
    def get_metadata_in_frame(data_dict, columns=None):
        """Get metadata in a pandas.DataFrame."""
        return pd.DataFrame(data_dict, columns=columns)

    @staticmethod
    def get_index(serie, string, contains=False, equals=False, between=False, as_boolean=False, reversed_boolean=False):
        """Get index or boolean array.

        Args:
            serie (pd.Series):
            string (str): Searching for string in serie
            contains (bool): False or True depending on purpose
            equals (bool): False or True depending on purpose
            as_boolean (bool): False or True depending on purpose
            reversed_boolean (bool): False or True depending on purpose
        """
        # FIXME Rename? you get either an index array or boolean array
        if contains:
            boolean = serie.str.contains(string, regex=False)
        elif equals:
            boolean = serie == string
        elif between:
            start_idx = serie[serie == string[0]].index[0]
            if string[1]:
                stop_idx = serie[serie == string[1]].index[0]
            else:
                stop_idx = 999999
            boolean = (serie.index > start_idx) & (serie.index < stop_idx)
        else:
            boolean = serie.str.startswith(string)

        if reversed_boolean:
            # boolean = boolean == False
            boolean = ~boolean

        if as_boolean:
            return boolean
        else:
            return np.where(boolean)[0]

    @staticmethod
    def get_series_object(obj):
        """Get one column with data, eg. pd.Serie."""
        if isinstance(obj, pd.DataFrame):
            # Not really necessary if you load file with argument header=None pd.read_csv(...,
            # header=None)
            s = pd.Series(obj.keys()[0])
            return s.append(obj[obj.keys()[0]], ignore_index=True)
        elif isinstance(obj, list):
            return pd.Series(obj)


class BaseReader:
    """Base structure for data readers."""

    def __init__(self, settings):
        """Initialize Base Class."""
        super().__init__(settings)

    def get_data(self, filenames=None, add_low_resolution_data=False, **kwargs):
        """Dummie method."""
        raise NotImplementedError

    def get_metadata(self, serie, *args, map_keys=False, **kwargs):
        """Dummie method."""
        raise NotImplementedError

    def merge_data(self, data, *args, resolution=None, **kwargs):
        """Dummie method."""
        raise NotImplementedError

    def setup_dataframe(self, serie, *args, metadata=None, **kwargs):
        """Dummie method."""
        raise NotImplementedError

    def setup_dictionary(self, fid, data, *args, keys=None, **kwargs):
        """Dummie method."""
        raise NotImplementedError


class UnitConverter:
    """Convert unit of given parameters.

    Plan:
    - input ctd-standard-format unit (rawdata unit)
        - dataframe metadata?
    - standard parameter unit (etc-file)
        - converting factor
    - converting function
        - pandas apply? numpy vecorize?
        - change [unit] of parameter name eg. CNDC_CTD [S/m]
          instead of CNDC_CTD [mS/cm]
    """

    def __init__(self, mapper, user):
        """Initialize and store mapper and user."""
        self.mapper = mapper
        self.user = user
        self.meta = None

    def update_meta(self, meta_serie):
        """Update meta information."""
        self.meta = meta_serie

    def convert_values(self, serie):
        """Convert unit of values in serie."""
        factor = self.get_conversion_factor(serie.name)
        decimals = self.get_number_of_decimals(serie.name)

        if serie.name.startswith('DENS'):
            serie = serie.astype(float) + factor
        else:
            serie = serie.astype(float) * factor
        serie = utils.rounder(serie, decimals=decimals)
        return serie

    def get_conversion_factor(self, parameter):
        """Return conversion factor (float) for the given parameter.

        Args:
            parameter (str): parameter with unit eg. 'DOXY_CTD [mg/l]'
        """
        return self.mapper[parameter].get('conversion_factor')

    def get_number_of_decimals(self, parameter):
        """Return number of decimals (integer) for the given parameter.

        Args:
            parameter (str): parameter with unit eg. 'DOXY_CTD [mg/l]'
        """
        return self.mapper[parameter].get('number_of_decimals')

    def set_new_parameter_name(self, serie):
        """Change name of serie if mapping is found."""
        new_name = self.mapper[serie.name].get('standard_parameter_name')
        serie.name = new_name or serie.name

    def rename_dataframe_columns(self, df):
        """Rename columns of the given dataframe based on the corresponding Series.name."""
        mapper = {key: self.mapper[key].get('standard_parameter_name') for key in df.columns if key in self.mapper}
        df.rename(columns=mapper, inplace=True)

    def append_conversion_comment(self):
        """Append comment self.meta."""
        time_stamp = utils.get_time_as_format(now=True, fmt='%Y%m%d%H%M')
        self.meta[len(self.meta) + 1] = '//COMNT_UNIT; UNIT CONVERSION PERFORMED BY {}; TIMESTAMP {}'.format(
            self.user, time_stamp)


class CorrectionFile(dict):
    """For now hardcoded parameters.."""

    # TODO make it more flexible.. loop over all columns of df? (corr_file) if parameter in datasets then --> ...

    def __init__(self, fid):
        """Initialize and store information from 'fid'-file."""
        super().__init__()
        df = load_txt(file_path=fid)
        for key, p_corr, s_corr in zip(df['key'], df['PRES_CTD [dbar]'], df['SALT_CTD [psu]']):
            self.setdefault(key, {})
            if p_corr:
                self[key]['PRES_CTD [dbar]'] = p_corr
            if s_corr:
                self[key]['SALT_CTD [psu]'] = s_corr


class DeltaCorrection:
    """BIAS correct data.

    If data deliverer has provided correction deltas (BIAS correction)
    for specific parameter profiles, we append that correction here.

    Eg.
        SALT_CTD:
            corr: 0.04
        PRES_CTD:
            corr: -0.2
    """

    def __init__(self, corr_obj=None, user=None, raw_format=False):
        """Initialize and store corr_obj and user.

        Args:
            corr_obj (dict):
                visit keys:
                    parameters:
                        correction delta
            user (str): Session user.
        """
        self.corr_obj = corr_obj
        self.user = user
        self.raw_format = raw_format
        self.meta = None
        self.serie_correction_comnt = {}

    def append_correction_comment(self, key_dict):
        """Append comment self.meta."""
        if self.serie_correction_comnt:
            time_stamp = utils.get_time_as_format(now=True, fmt='%Y%m%d%H%M')
            corr_template_str = '//COMNT_CORRECTION; PROFILE CORRECTIONS PERFORMED BY {}; TIMESTAMP {}; {}-{}: {}'
            comnt_list = []

            for para, item in self.serie_correction_comnt.items():
                comnt = corr_template_str.format(
                    self.user, time_stamp, para, item['type'], item['value']
                )
                if self.raw_format:
                    comnt_list.append(comnt)
                else:
                    # Data according to datahost standard format.
                    self.meta[len(self.meta) + 1] = comnt
            if self.raw_format:
                self.meta['COMNTS'] = comnt_list

        self.serie_correction_comnt = {}

    def correct_dataset(self, ds):
        """Loop over datasets and correct data series."""
        print('correction...')
        for key, item in ds.items():
            self.update_meta(item['metadata'])
            self._correct(item['data'], key)
            self.append_correction_comment(self.corr_obj.get(key))
        print('correction completed!')

    def _correct(self, df, key):
        """Correct the given pd.Serie.

        Args:
            df (pd.DataFrame): Data.
            key (str): visit key. Eg.'ctd_profile_20180122_7798_5051'

        'B1201207.TOB': {
            'SALT_CTD': {'type': 'bias', 'value': 0.01},
            'PRES_CTD': {'type': 'bias', 'value': -0.04},
            'DO_mg': {
                'type': 'equation',
                'value': 'OXYGEN_MG + ((0.14*TEMP – 0.0045*TEMP**2 – 0.2)*(OXYGEN_MG/10))',
                'mapping': {'OXYGEN_MG': 'DO_mg', 'TEMP': 'TEMP_CTD'}
            },
            'DOXY_CTD': {
                'type': 'equation',
                'value': 'DO_mg * 0.7',
                'mapping': {'DO_mg': 'DO_mg'}
            }
        }
        """
        def get_doxy_sat(doxy, salt, temp):
            """Calculate oxygen saturation."""
            if doxy and salt and temp:
                doxy = float(doxy)
                if doxy < 0:
                    doxy = 0.
                return doxy / seawater.satO2(float(salt), float(temp)) * 100
            else:
                return np.nan

        visit_corr = self.corr_obj.get(key)
        for para, item in visit_corr.items():
            if para in df:
                nr_decimals = len(df[para][0].split('.')[1])

                if item['type'] == 'bias':
                    s = df[para].astype(float)
                    s = s + item['value']
                elif item['type'] == 'equation' and para == 'DOXY_SAT_CTD':
                    s = df[item['mapping'].values()].apply(lambda x: get_doxy_sat(*x), axis=1)
                elif item['type'] == 'equation':
                    s = df[item['mapping'].values()].apply(lambda x: eval(
                        item.get('value'), {key: float(x[i]) for i, key in enumerate(item['mapping'].keys())}
                    ), axis=1)
                else:
                    raise ValueError('Could not identify correction type: {}'.format(item['type']))

                df[para] = s.apply(lambda x: utils.round_value(x, nr_decimals=nr_decimals))

                self.serie_correction_comnt[para] = item

    def update_meta(self, meta_serie):
        """Update meta serie."""
        self.meta = meta_serie


class MetaHandler(SeriesHandler):
    """We intend to write some more code here. Right?"""
