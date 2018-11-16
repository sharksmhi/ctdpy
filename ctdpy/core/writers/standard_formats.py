# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 17:00:35 2018

@author: a002028
"""
import pandas as pd
from core.data_handlers import DataFrameHandler
from core.data_handlers import SeriesHandler
from core.writers.txt_writer import TxtWriter
import utils


class StandardCTDWriter(SeriesHandler, DataFrameHandler):
    """
    """
    def __init__(self, settings):
        super().__init__(settings)

        # self.setup_standard_format()
        self.writer = self._get_writer_settings()
        self.txt_writer = TxtWriter()

    def write(self, datasets):
        """
        Calls methods in order to strucure data according to standard and then writes to standard output format
        :param datasets: All loaded datasets [pd.DataFrame(s), pd.Series]
        """
        meta = self.get_metadata_sets(datasets)
        data = self.get_datasets(datasets)

        self.setup_metadata_information(meta)

        for dataset in data:
            for fid, item in dataset.items():
                instrument_metadata = self._get_instrument_metadata(item.get('raw_format'),
                                                                    separator=self.writer['separator_metadata'])
                metadata = self.extract_metadata(fid, separator=self.writer['separator_metadata'])
                metadata_df = self.extract_metadata_dataframe(fid)
                self.reset_index(metadata_df)
                self._update_visit_info(metadata_df)

                data_df = self._get_data_columns(item['hires_data'], metadata_df)
                data_series = self._get_data_serie(data_df, separator=self.writer['separator_data'])

                self._write(fid, instrument_metadata, metadata, data_series)

    def _write(self, fid, instrument_metadata, metadata, data_series):
        """
        :param fid: Original file name
        :param instrument_metadata: pd.Series, CTD-cast specific data
        :param metadata: pd.Series, CTD-cast specific data
        :param data_series: pd.Series, CTD-cast specific data
        :return: CTD-cast text file according to standard format
        """
        out_serie = pd.Series([])
        out_serie = out_serie.append([self.template_format,
                                      self.delimiters['meta'],
                                      self.delimiters['data'],
                                      metadata,
                                      self.sensorinfo,
                                      self.information,
                                      instrument_metadata,
                                      data_series])

        save_path = self._get_save_path(fid)

        self.txt_writer.write_with_numpy(data=out_serie, save_path=save_path)

    def setup_metadata_information(self, meta):
        """
        Olala, here we go..
        Sets up standard metadata formats that later is writable..
        :param meta: Contains pd.DataFrame(s) of metadata delivered to datahost
                     in excel spreadsheets [Metadata, Sensorinfo, Information]
        """
        # TODO sould be able to handle multiple metadatasets? (.xlsx delivery files)
        self.template_format = self._get_template_format(meta[0])
        self.delimiters = self._get_delimiters()
        self.df_metadata = self._get_reduced_dataframe(meta[0]['Metadata'])
        self.delivery_note = self._get_delivery_note(meta[0]['Förklaring'])
        self.df_sensorinfo = self._get_reduced_dataframe(meta[0]['Sensorinfo'])
        self.sensorinfo = self._get_sensorinfo_serie(separator=self.writer['separator_metadata'])
        self.information = self._get_information_serie(meta[0]['Information'],
                                                       separator=self.writer['separator_metadata'])

    def _get_template_format(self, meta):
        """
        # TODO adjust reader, get format from tamplate ('Förklaring').. ö..
        :return: Standard format of template output
        """
        return pd.Series([self.writer['prefix_format']+'=CTD'])

    def _get_delimiters(self):
        """
        # FIXME Redo and delete hardcoded parts.. Get better solution than '\ t'.replace(' ','') for tabb-sign
        # FIXME self.writer['separator_data']])}
        :return: dictionary
        """

        return {'meta': pd.Series([''.join([self.writer['prefix_metadata_delimiter'], '=', self.writer['separator_metadata']])]),
                'data': pd.Series([''.join([self.writer['prefix_data_delimiter'], '=', '\ t'.replace(' ', '')])])}

    def _get_delivery_note(self, delivery_info):
        """

        :param delivery_info: pd.DataFrame ("Förklarings-flik")
        :return:
        """
        # FIXME Could be prettier..
        info = {}
        xy_index = self._get_index(delivery_info, check_values=['MYEAR', 'DTYPE'])
        for key, value in zip(delivery_info.iloc[xy_index[0][0]:, xy_index[1][0]],
                              delivery_info.iloc[xy_index[0][0]:, xy_index[1][0] + 2]):
            if not pd.isnull(key):
                info[key] = value
            else:
                break

        # Check for info in self.df_metadata
        for key in ['MYEAR', 'ORDERER', 'PROJ']:
            if not info[key]:
                info[key] = ','.join(self.df_metadata[key].unique())

        return info

    @staticmethod
    def _get_index(df, check_values=None):
        """
        :param df: pd.DataFrame
        :param check_values: Checklist in order of importance
        :return: numpy index array (array([15], dtype=int64), array([0], dtype=int64))
        """
        for value in check_values:
            if any(df == value):
                return utils.get_index_where_df_equals_x(df, value)
        return None

    def extract_metadata(self, filename, separator=None):
        """
        :param filename: str, filename of raw data
        :param separator: str, separator to separate row values
        :return: pd.Series, Lists according to template standards
        """
        meta = self.extract_metadata_dataframe(filename)
        self.reset_index(meta)
        meta = meta.iloc[0]
        serie = pd.Series(self.df_metadata.columns)

        # FutureWarning if not join is set to 'left' instead of None
        serie = serie.str.cat(meta, sep=separator, join='left')
        serie = serie.radd(self.writer['prefix_metadata'] + separator)
        return serie

    def extract_metadata_dataframe(self, filename):
        """
        Used in order to fill out data columns..
        :param filename: str, filename of raw data
        :return: 1 row pd.DataFrame
        """
        boolean = self.get_index(self.df_metadata['FILE_NAME'], filename,
                                 equals=True, as_boolean=True)
        return self.df_metadata.loc[boolean, :]

    @staticmethod
    def _get_reduced_dataframe(df):
        """
        Exclude empty column "Tabellhuvud:"
        :param df: pd.DataFrame
        :return: Reduced pd.DataFrame
        """
        if 'Tabellhuvud:' in df:
            df.pop('Tabellhuvud:')
        return df

    def _get_sensorinfo_serie(self, separator=None):
        """

        :param separator: str, separator to separate row values
        :return:
        """
        out_info = [pd.Series(self.df_sensorinfo.columns).str.cat(sep=separator)]
        for index, row in self.df_sensorinfo.iterrows():
            out_info.append(row.str.cat(sep=separator))

        out_info = self.get_series_object(out_info)
        out_info = out_info.radd(self.writer['prefix_sensorinfo'] + separator)
        return out_info

    def _get_information_serie(self, info, separator=None):
        """

        :param info: pd.Series
        :param separator: str, separator to separate row values
        :return: Lists according to template standards
        """
        out_info = [pd.Series(info.columns).str.cat(sep=separator)]
        for index, row in info.iterrows():
            out_info.append(row.str.cat(sep=separator))

        out_info = self.get_series_object(out_info)
        out_info = out_info.radd(self.writer['prefix_info'] + separator)
        return out_info

    def _get_instrument_metadata(self, serie, separator=None):
        """
        Sorts out instrument metadata from serie (everything but data)
        :param serie: pd.Series, Data in raw format
        :param separator: str, separator to separate row values
        :return: Lists according to template standards
        """
        end_idx = self.get_index(serie, self.writer['identifier_instrument_metadata_end'])
        out_info = serie.iloc[:end_idx[0]+1]
        out_info = out_info.radd(self.writer['prefix_instrument_metadata'] + separator)
        return out_info

    def _get_data_serie(self, df, separator=None):
        """

        :param df: pd.DataFrame, Column data
        :return: pd.Series, row data merged with separator
        """
        out_info = [pd.Series(df.columns).str.cat(sep=separator)]
        for index, row in df.iterrows():
            out_info.append(row.str.cat(sep=separator))

        out_info = self.get_series_object(out_info)
        return out_info

    def _get_data_columns(self, data, metadata):
        """
        Merge column data with extended metadata (multiply selected metadata fields to "data"-column length)
        :param data: pd.DataFrame, Hi resolution
        :param metadata: 1 row pd.DataFrame
        :return: pd.DataFrame
        """
        header = self.set_header()
        dictionary = {key: [] for key in header}
        column_length = data.shape[0]

        for key in dictionary:
            if key in data:
                dictionary[key] = data[key]
                continue
            elif key in metadata:
                value = metadata.at[0, key]
            else:
                value = self.get_property_value(key)

            dictionary[key] = [value] * column_length

        df = pd.DataFrame(data=dictionary, columns=header).fillna('')
        mapp_dict = self._get_header_mapping_dict()
        df = self._rename_columns_of_dataframe(df, mapp_dict)

        return df

    def _get_header_mapping_dict(self):
        """
        Creates dictionary with column name as key and new column name as value
        :return: Mapping dictionary for header transformation
        """
        mapp_dict = {}
        for para, unit in zip(self.df_sensorinfo.PARAM, self.df_sensorinfo.MUNIT):
            wrapped_unit = ''.join(['[', unit, ']'])
            mapp_dict[para] = ' '.join([para, wrapped_unit])

        return mapp_dict

    def set_header(self):
        """
        Adds specified parameters from sensorinfo (Excel spreadsheet) to the standard "Visit info header"
        :return: List, Complete header for CTD standard format
        """
        parameters_list = self.get_parameters_from_sensorinfo()
        return self.writer['standard_data_header'] + parameters_list

    def get_parameters_from_sensorinfo(self):
        """
        :return: All parameters from sensorinfo including Q-flags
        """
        outlist = []
        for param in self.df_sensorinfo['PARAM'].values:
            outlist.append(param)
            outlist.append('Q_'+param)
        return outlist

    def _get_writer_settings(self):
        """
        :return: Specialized writer settings
        """
        return self.settings.writers['ctd_standard_template']['writer']

    @staticmethod
    def get_metadata_sets(datasets):
        """
        Sorts out metadata
        :param datasets: All loaded datasets
        :return: List of datasets (meta)
        """
        # TODO presumably we might need to handle other metadata formats than xlsx?
        out_sets = []
        for dset in datasets:
            for key in dset:
                if key.endswith('.xlsx'):
                    out_sets.append(dset[key])
        return out_sets

    @staticmethod
    def get_datasets(datasets):
        """
        Sorts out data
        :param datasets: All loaded datasets
        :return: List of datasets (data)
        """
        out_sets = []
        for dset in datasets:
            for key in dset:
                if not key.endswith('.xlsx'):
                    out_sets.append(dset)
                    break
        return out_sets

    def _get_save_path(self, fid):
        """
        :param fid: str, 'x.cnv'
        :return: save path to file
        """
        if not hasattr(self, 'data_path'):
            self._set_data_path()
            utils.check_path(self.data_path)

        file_path = ''.join([self.data_path,
                             self.writer.get('filename'),
                             fid.split('.')[0],
                             self.writer.get('extension_filename')])
        return file_path

    def _set_data_path(self):
        """
        :return:
        """
        time_now = utils.get_datetime_now(fmt='%Y%m%d_%H%M%S')
        self.data_path = ''.join([self.settings.settings_paths.get('export_path'), time_now, '/'])

    def _update_visit_info(self, metadata):
        """
        :param metadata: 1 row pd.DataFrame
        :return: Update visit info properties of parent class
        """
        self._update_visit_datetime_object(metadata)
        self._update_visit_position(metadata)
        self._update_visit_cruise_name(metadata)
        self._update_visit_station(metadata)

    def _update_visit_cruise_name(self, metadata):
        """
        Get ship code and cruise number from metadata and update cruise_dictionary
        :param metadata: 1 row pd.DataFrame
        :return: Update cruise dictionary which in turn updates
                 cruise properties of BaseFileHandler (META base class)
        """
        shipc = metadata.at[0, 'SHIPC']
        cruise_no = metadata.at[0, 'CRUISE_NO']
        self.update_cruise(shipc, cruise_no)

    def _update_visit_datetime_object(self, metadata):
        """
        Get date and time strings in order to update datetime object
        :param metadata: 1 row pd.DataFrame
        :return: Update datetime object which in turn updates
                 date and time properties of BaseFileHandler (META base class)
        """
        sdate = metadata.at[0, 'SDATE']
        stime = metadata.at[0, 'STIME']
        self.update_datetime_object(sdate, stime)

    def _update_visit_position(self, metadata):
        """
        Get LATIT and LONGI from metadata and update position_dictionary
        :param metadata: 1 row pd.DataFrame
        :return: Update position_dictionary which in turn updates
                 position properties of BaseFileHandler (META base class)
        """
        lat = metadata.at[0, 'LATIT']
        lon = metadata.at[0, 'LONGI']
        self.update_position(lat, lon)

    def _update_visit_station(self, metadata):
        """
        Update station
        :param metadata: 1 row pd.DataFrame
        :return: Update station name which in turn updates
                 statn properties of BaseFileHandler (META base class)
        """
        statn = metadata.at[0, 'STATN']
        self.update_station_name(statn)
