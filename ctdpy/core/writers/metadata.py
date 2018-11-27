# -*- coding: utf-8 -*-
"""
Created on 2018-11-20 08:55

@author: Johannes Johansson

"""
import pandas as pd
import utils
from core.data_handlers import DataFrameHandler
from core.data_handlers import SeriesHandler
from core.writers.xlsx_writer import XlsxWriter

class MetadataWriter(SeriesHandler, DataFrameHandler):
    """

    """
    def __init__(self, settings):
        super().__init__(settings)
        self.xlsx_writer = XlsxWriter()
        self.template =

    def load_template(self):
        """
        Load Delivery Template
        :return:
        """
        reader = self.get_reader()
        #TODO **kwargs
        empty_template = reader(self.settings.templates['phyche']['template'].get('file_path'),
                                sheet_name=self.settings.templates['phyche']['template'].get('data_sheetname'),
                                header_row=self.settings.templates['phyche']['template'].get('header_row'))

        self.template = Template(empty_template)

    def write(self, metadata):
        """

        :param metadata: pd.DataFrame, loaded metadata
        :return: exports a Delivery Template Excel file
        """

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
                data_series = self._append_information(self.template_format,
                                                       self.delimiters['meta'],
                                                       self.delimiters['data'],
                                                       metadata,
                                                       self.sensorinfo,
                                                       self.information,
                                                       instrument_metadata,
                                                       data_series)
                self._write(fid, data_series)

        self._write_delivery_note()

    def _write_delivery_note(self):
        """
        :return: Text file with "delivery_note"
        """
        serie = pd.Series(self.writer['standard_delivery_note_header'])
        info = pd.Series([self.delivery_note[self.writer['mapper_delivery_note'][key]]
                          for key in serie])

        serie = serie.str.cat(info, join=None,
                              sep=self.writer['separator_delivery_note'])
        self._write('delivery_note', serie)

    def _write(self, fid, data_series):
        """
        :param fid: Original file name
        :return: CTD-cast text file according to standard format
        """
        save_path = self._get_save_path(fid)
        self.txt_writer.write_with_numpy(data=data_series, save_path=save_path)


    def setup_metadata_information(self, meta):
        """"""
        self.df_metadata = self._get_reduced_dataframe(meta[0]['Metadata'])
        self.delivery_note = self._get_delivery_note(meta[0]['Förklaring'])
        self.template_format = self._get_template_format()

    def _get_template_format(self):
        """
        # TODO adjust reader, get format from tamplate ('Förklaring').. ö..
        :return: Standard format of template output
        """
        return pd.Series([''.join([self.writer['prefix_format'], '=', self.delivery_note['DTYPE']])])
        # return pd.Series([self.writer['prefix_format']+'=CTD'])

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

    def _get_writer_settings(self):
        """
        :return: Specialized writer settings
        """
        return self.settings.writers['ctd_standard_template']['writer']

    def _get_save_path(self, fid):
        """
        :param fid: str, 'x.cnv'
        :return: save path to file
        """
        if not hasattr(self, 'data_path'):
            self._set_data_path()
            utils.check_path(self.data_path)

        if 'delivery_note' in fid or 'information' in fid or 'sensorinfo' in fid:
            file_prefix = ''
        else:
            file_prefix = self.writer.get('filename')

        file_path = ''.join([self.data_path,
                             file_prefix,
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























