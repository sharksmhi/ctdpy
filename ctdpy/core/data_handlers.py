# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 13:26:05 2018

@author: a002028
"""
import pandas as pd
import numpy as np
from ctdpy.core.readers.file_handlers import BaseFileHandler
from ctdpy.core import utils
import warnings
warnings.filterwarnings("ignore", 'This pattern has match groups')


class DataFrameHandler(BaseFileHandler):
    """
    #TODO perhaps we should move staticmethods (.get_"datetimes", _"position" to utils?
    """    
    def __init__(self, settings):
        super().__init__(settings)
        self.settings = settings

    def map_column_names_of_dataframe(self, df):
        """
        :param df: pd.DataFrame
        :return: pd.DataFrame
        """
        map_dict = self.settings.pmap.get_parameter_mapping(df.columns.tolist())

        return self._rename_columns_of_dataframe(df, map_dict)

    @staticmethod
    def _rename_columns_of_dataframe(df, mapping_dict):
        """
        :param df: pd.DataFrame
        Rename dataframe columns
        :param mapping_dict: Dictionary with old names as keys and new names as values
        :return: pd.DataFrame
        """
        return df.rename(index=str, columns=mapping_dict)

    @staticmethod
    def add_metadata_to_frame(df, meta, len_col=None):
        """
        :param df: pd.DataFrame
        :param meta: Dictionary with metadata
        :param len_col: Length of DataFrame columns
        :return: pd.DataFrame
        """
        df_meta = pd.DataFrame({k: [meta[k]] * len_col for k in meta})
        df = df.reset_index(drop=False)  # orginal index of df is saved
        df = pd.concat([df, df_meta], axis=1)
        return df

    @staticmethod
    def get_data_header(df):
        """
        :param df: pd.DataFrame
        :return: list of dataframe column names
        """
        return df.columns

    @staticmethod
    def get_index(data, key, string):
        """

        :param data: pd.DataFrame or dictionary
        :param key: str
        :param string: str, search for string
        :return: array with indices
        """
        # FIXME use pandas isin instead.. booleans..
        return np.where(data[key] == string)[0]

    @staticmethod
    def get_datetime_format(df, sdate_key=None, stime_key=None):
        """
        Uses date and time to create array with datetime object
        :param df: pd.DataFrame
        :param sdate_key: str
        :param stime_key: str
        :return: datetime object
        """
        datetime_format = np.vectorize(utils.get_datetime)(df[sdate_key], df[stime_key])
        return datetime_format

    @staticmethod
    def get_sdate(datetime_obj, fmt='%Y-%m-%d'):
        """
        :param datetime_obj: datetime object
        :param fmt: str
        :return: str according to fmt
        """
        stime = np.vectorize(utils.get_format_from_datetime_obj)(datetime_obj, fmt)
        return stime

    @staticmethod
    def get_stime(datetime_obj, fmt='%H:%M:%S'):
        """
        :param datetime_obj: datetime object
        :param fmt: str
        :return: str according to fmt
        """
        stime = np.vectorize(utils.get_format_from_datetime_obj)(datetime_obj, fmt)
        return stime

    @staticmethod
    def get_position_decimal_degrees(pos_serie):
        """
        Uses numpy.vectorize to transform position format DDMM.mm into DD.dddd
        :param pos_serie: pd.Series of coordinates in format DDMM.mm
        :return: pd.Series of coordinates in format DD.dddd
        """
        pos = np.vectorize(utils.decmin_to_decdeg)(pos_serie)
        return pos

    @staticmethod
    def reset_index(df):
        """
        Resets the index array for the dataframe in question
        :param df: pd.DataFrame
        :return: DataFrame with index array from 0 --> x
        """
        df.reset_index(inplace=True, drop=True)


class SeriesHandler(BaseFileHandler):
    """
    Handles object: pandas.Series
    """    
    def __init__(self, settings):
        super().__init__(settings)
        self.settings = settings

    def update_datetime_object(self, date_string, time_string):
        """
        :param date_string: str, YYYY-MM-DD
        :param time_string: str, HH:MM:SS
        :return: Using property.setter
        """
        datetime_obj = utils.get_datetime(date_string, time_string)
        self.year = datetime_obj
        self.month = datetime_obj
        self.day = datetime_obj
        self.hour = datetime_obj
        self.minute = datetime_obj
        self.second = datetime_obj

    def update_position(self, lat, lon):
        """
        :param lat: str, Latitude DDMM.mmm
        :param lon: str, Longitude DDMM.mmm
        :return: Using property.setter
        """
        self.latitude_dd = lat
        self.longitude_dd = lon

    def update_cruise(self, shipc, cruise_no):
        """
        myear_shipc_cruise_no, where myear is taken from property
        :param shipc: ship code
        :param cruise_no: Specific cruise number, YYYY_SHIP_NNNN
        :return:
        """
        if cruise_no:
            self.cruise = [self.year, shipc, cruise_no]
        else:
            self.cruise = ''

    def update_station_name(self, statn):
        """
        :param statn: Station name at visit
        :return: Using property.setter
        """
        self.station = statn

    def get_data_header(self, data, dataset=None, idx=1, first_row=False):
        """
        Get header from identifier in settings file.
        Assumes all values shall be taken from 'idx' after splitting
        :param data: pd.Series
        :param dataset: str
        :param idx: Default 1 due to Standard Seabird output
                    Example: '=' is the splitter in this specific case
                    # name 2 = t090C: Temperature [ITS-90, deg C]
                    head will then be 't090C: Temperature [ITS-90, deg C]'
        :return: list of column names (header)
        """
        identifier_header = self.settings.datasets[dataset]['identifier_header']
        reversed = '~' in identifier_header
        index = self.get_index(data, identifier_header.replace('~', ''), reversed_boolean=reversed)
        splitter = self.settings.datasets[dataset].get('separator_header')
        if first_row:
            if splitter == None or splitter == 'None':
                header = data[index].iloc[0].split()
            else:
                header = data[index].iloc[0].split(splitter)
        else:
            header = [head.split(splitter)[idx].strip() for head in data[index]]

        header = self.map_doublet_columns(header)

        return header

    @staticmethod
    def map_doublet_columns(header):
        """
        :param header:
        :return:
        """
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
        """
        Get data from pd.Series. separates row values in series into columns within the
        DataFrame
        :param series: pd.Series, data
        :param columns: list, column names
        :param dataset: str, reader specific dataset. Determines how to handle data format
        :return: pd.DataFrame
        """
        #FIXME NOOOO!! not the way to go! if anything, add reversed as input argument! let the identifier be clean!
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
        """
        :param series: pd.Series, contains metadata
        :param keys: List of keys to search for
        :param identifier: str
        :param separator: str
        :return: Dictionary
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
                        #FIXME do we really want this? better to SLAM down hard with a KeyError/ValueError?
                        meta = value[value.index(key)+len(key):].strip()

                    if meta:
                        meta_dict.setdefault(key, meta)
        else:
            return series.loc[boolean_startswith]
        return meta_dict

    @staticmethod
    def get_metadata_in_frame(data_dict, columns=None):
        """
        :param data_dict: dictionary
        :param columns: list, column names
        :return: pd.DataFrame
        """
        return pd.DataFrame(data_dict, columns=columns)

    @staticmethod
    def get_index(serie, string, contains=False, equals=False, as_boolean=False, reversed_boolean=False):
        """
        #FIXME Rename? you get either an index array or boolean array
        :param serie: pd.Series
        :param string: str, searching for string in serie
        :param contains: False or True depending on purpose
        :param equals: False or True depending on purpose
        :param as_boolean: False or True depending on purpose
        :param reversed_boolean: False or True depending on purpose
        :return: numpy index array or boolean list
        """
        if contains:
            # contains
            boolean = serie.str.contains(string, regex=False)
        elif equals:
            # equals
            boolean = serie == string
        else:
            # startswith
            boolean = serie.str.startswith(string)

        if reversed_boolean:
            boolean = boolean == False

        if as_boolean:
            return boolean
        else:
            return np.where(boolean)[0]

    @staticmethod
    def get_series_object(obj):
        """
        One column with data
        :param obj: pd.DataFrame or list
        :return: pd.Series
        """
        if isinstance(obj, pd.DataFrame):
            s = pd.Series(obj.keys()[0])
            return s.append(obj[obj.keys()[0]], ignore_index=True)
        elif isinstance(obj, list):
            return pd.Series(obj)


class BaseReader(object):
    """
    Base structure for data readers
    """
    def __init__(self, settings):
        super().__init__(settings)

    def get_data(self, filenames=None, add_low_resolution_data=False):
        """
        :param filenames:
        :param add_low_resolution_data:
        :return:
        """
        raise NotImplementedError

    def get_metadata(self, serie, map_keys=False):
        """
        :param serie:
        :param map_keys:
        :return:
        """
        raise NotImplementedError

    # @staticmethod
    # def get_reader_instance():
    #     """
    #     :return:
    #     """
    #     raise NotImplementedError

    def merge_data(self, data, resolution=None):
        """
        :param data:
        :param resolution:
        :return:
        """
        raise NotImplementedError

    def setup_dataframe(self, serie):
        """
        :param serie:
        :return:
        """
        raise NotImplementedError

    def setup_dictionary(self, fid, data):
        """
        :param fid:
        :param data:
        :return:
        """
        raise NotImplementedError


class DataTransformation(object):
    """
    - Append multiple dataframes into one
    - Add columns
    - ...
    """
    def __init__(self):
        self.df = pd.DataFrame(index=[])

    def append_dataframes(self, dataframes):
        """"""
        assert type(dataframes) == list

        print('appending dataframes..')
        for df in dataframes:
            self.df = self.df.append(df)

        self.df.reset_index(drop=True, inplace=True)
        print('dataframes appended!')

    def add_columns(self):
        """"""
        self.add_date_column()
        self.add_time_column()

    def add_color_columns(self, qflags, mapper=None):
        """"""
        mapper = mapper or {'Q0_TEMP_CTD': 'color_x1',
                            'Q0_TEMP2_CTD': 'color_x1b',
                            'Q0_SALT_CTD': 'color_x2',
                            'Q0_SALT2_CTD': 'color_x2b',
                            'Q0_DOXY_CTD': 'color_x3',
                            'Q0_DOXY2_CTD': 'color_x3b'}
        for qf in qflags:
            color_key = mapper.get(qf)
            if 'b' in color_key:
                color = 'purple'
            else:
                color = 'navy'
            self.df[color_key] = self.df[qf].fillna('').apply(lambda x: color if 'B' not in x else 'red')

    def add_date_column(self):
        """"""
        self.df['SDATE'] = self.df[['YEAR', 'MONTH', 'DAY']].astype(str).apply('-'.join, axis=1)

    def add_time_column(self):
        """"""
        self.df['STIME'] = self.df[['HOUR', 'MINUTE']].astype(str).apply(':'.join, axis=1)

    def set_column_format(self, **kwargs):
        """
        :param kwargs: {'para_1': float,
                        'para_2': str}
        :return:
        """
        for key, value in kwargs.items():
            if key in self.df:
                try:
                    self.df[key] = self.df[key].astype(value)
                except ValueError:
                    self.df[key] = self.df[key].replace('', np.nan).astype(value)

    def get_dataframe(self, columns=None):
        """
        :param columns:
        :return:
        """
        if not columns:
            return self.df
        else:
            return self.df[columns]

    @staticmethod
    def add_keys_to_datasets(datasets):
        """"""
        for key_name in datasets[0].keys():
            datasets[0][key_name]['data']['KEY'] = key_name.strip('ctd_profile|.txt')


class UnitConverter(object):
    """
    Plan:
    - input ctd-standard-format unit (rawdata unit)
        - dataframe metadata?
    - standard parameter unit (etc-file)
        - converting factor
    - converting function
        - pandas apply? numpy vecorize?
        - change [unit] of parameter name eg. CNDC_CTD [S/m] instead of CNDC_CTD [mS/cm]
    """
    def __init__(self, mapper, user):
        self.mapper = mapper
        self.user = user
        self.meta = None

    def update_meta(self, meta_serie):
        """
        :param meta_serie:
        :return:
        """
        self.meta = meta_serie

    def convert_values(self, serie):
        """
        :param serie: pandas.Series
        :return:
        """
        factor = self.get_conversion_factor(serie.name)
        decimals = self.get_number_of_decimals(serie.name)

        serie = serie.astype(float) * factor
        serie = utils.rounder(serie, decimals=decimals)

        return serie

    def get_conversion_factor(self, parameter):
        """
        :param parameter: str, parameter with unit eg. DOXY_CTD [mg/l]
        :return: float, conversion factor
        """
        return self.mapper[parameter].get('conversion_factor')

    def get_number_of_decimals(self, parameter):
        """
        :param parameter: str, parameter with unit eg. DOXY_CTD [mg/l]
        :return: int, number_of_decimals
        """
        return self.mapper[parameter].get('number_of_decimals')

    def set_new_parameter_name(self, serie):
        """
        Change name of serie if mapping is found
        :param serie: pandas.Series
        """
        new_name = self.mapper[serie.name].get('standard_parameter_name')
        serie.name = new_name or serie.name

    @staticmethod
    def rename_dataframe_columns(df):
        """
        #TODO move to utils?
        :param df: pandas.DataFrame
        :return: Renames columns of dataframe based on the corresponding Series.name
        """
        df.rename(columns={key: df[key].name for key in df.columns}, inplace=True)

    def append_conversion_comment(self):
        """
        :param metadata:
        :return:
        """
        time_stamp = utils.get_time_as_format(now=True, fmt='%Y%m%d%H%M')
        self.meta[len(self.meta) + 1] = '//COMNT_UNIT; UNIT CONVERSION PERFORMED BY {}; TIMESTAMP {}'.format(
            self.user, time_stamp)


if __name__ == "__main__":
    df = pd.DataFrame({'a': [1, 2, 3, 4, 5]})
    uc = UnitConverter(None, None)

    s = df['a']
    s.name = 'hej'

    uc.rename_dataframe_columns(df=df)
    print(df)
