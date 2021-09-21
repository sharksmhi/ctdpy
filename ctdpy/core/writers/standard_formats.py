# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 17:00:35 2018

@author: a002028
"""
import os
import pandas as pd
from ctdpy.core.data_handlers import DataFrameHandler
from ctdpy.core.data_handlers import SeriesHandler
from ctdpy.core.writers.txt_writer import TxtWriter
from ctdpy.core import utils


class StandardCTDWriter(SeriesHandler, DataFrameHandler):
    """Writer to write CTD data to the standrad SMHI CTD format."""

    def __init__(self, settings):
        """Initialize and store the settings object."""
        super().__init__(settings)
        self._file_name = None
        # self.setup_standard_format()
        self.writer = self._get_writer_settings()
        self.txt_writer = TxtWriter()

        self._sensorinfo_boolean = False
        self.std_format = False

    def write(self, datasets):
        """Cunduct the writing process.

        Call methods in order to strucure data according to standard and then writes to standard output format
        Args:
            datasets: All loaded datasets [pd.DataFrame(s), pd.Series]
        """
        self._check_dataset_format(datasets)
        if self.std_format:
            self._redirect_to_data_update(datasets)
        else:
            meta = self.get_metadata_sets(datasets)
            data = self.get_datasets(datasets)
            self.setup_metadata_information(meta)

            for dataset in data:
                for fid, item in dataset.items():
                    # print(item['metadata'])
                    self.sensorinfo_boolean = item['metadata'].get('INSTRUMENT_SERIE')
                    instrument_metadata = self._get_instrument_metadata(item.get('raw_format'),
                                                                        separator=self.writer['separator_metadata'],
                                                                        data_identifier=item.get('identifier_data'))
                    metadata = self.extract_metadata(fid, separator=self.writer['separator_metadata'])
                    metadata_df = self.extract_metadata_dataframe(fid)
                    self.reset_index(metadata_df)
                    self._update_visit_info(metadata_df)
                    data_df = self._get_data_columns(item['data'], metadata_df)
                    data_series = self._get_data_serie(data_df, separator=self.writer['separator_data'])
                    data_series = self._append_information(self.template_format,
                                                           self.delimiters['meta'],
                                                           self.delimiters['data'],
                                                           metadata,
                                                           self.sensorinfo[item['metadata'].get('INSTRUMENT_SERIE')],
                                                           self.information,
                                                           instrument_metadata,
                                                           data_series)
                    self._write(fid, data_series)

            self._write_delivery_note()
            self._write_metadata()
            self._write_sensorinfo()
            self._write_information()

    def _write_delivery_note(self):
        """Write delivery information to text file."""
        serie = pd.Series(self.writer['standard_delivery_note_header'])
        info = []
        for key in serie:
            info.append(self.delivery_note.get(self.writer['mapper_delivery_note'].get(key), ''))
        info = pd.Series(info)

        serie = serie.str.cat(
            info,
            join=None,
            sep=self.writer['separator_delivery_note'],
        )
        self._write('delivery_note', serie)

    def _write_metadata(self):
        """Write metadata information to text file."""
        save_path = self._get_save_path('metadata')
        self.txt_writer.write_with_pandas(data=self.df_metadata,
                                          header=True,
                                          save_path=save_path)

    def _write_sensorinfo(self):
        """Write sensor information to text file."""
        save_path = self._get_save_path('sensorinfo')
        self.txt_writer.write_with_pandas(data=self.df_sensorinfo,
                                          header=True, save_path=save_path)

    def _write_information(self):
        """Write "other" information to text file."""
        exclude_str = self.writer['prefix_info'] + self.writer['separator_metadata']
        self._write('information', self.information.str.replace(exclude_str, ''))

    def _write(self, fid, data_series):
        """Write CTD-cast text file according to standard format to file."""
        save_path = self._get_save_path(fid)
        self.txt_writer.write_with_numpy(data=data_series, save_path=save_path)

    def _add_new_information_to_metadata(self):
        """Add information to metadata (originally loaded from excel-template (delivery))"""
        prefix = self.writer.get('filename')
        suffix = self.writer.get('extension_filename')

        new_column = self.df_metadata[['SDATE', 'SHIPC', 'SERNO']].apply(
            lambda x: prefix + '_'.join(x) + suffix,
            axis=1,
        )
        new_column = new_column.str.replace('-', '')
        self.df_metadata.insert(self.df_metadata.columns.get_loc('FILE_NAME') + 1,
                                'FILE_NAME_DATABASE', new_column)

    def _adjust_data_formats(self):
        """Adjust foramts."""
        self.file_name = self.df_metadata['FILE_NAME']  # property.setter, returns upper case filenames
        self.df_metadata['SDATE'] = self.df_metadata['SDATE'].str.replace(' 00:00:00', '')
        self.df_metadata['STIME'] = self.df_metadata['STIME'].apply(lambda x: x[:5])
        self.df_metadata['SERNO'] = self.df_metadata['SERNO'].apply(lambda x: x.zfill(4))

    def _append_information(self, *args):
        """Append and return information as pd.Serie."""
        out_serie = pd.Series([])
        out_serie = out_serie.append([serie for serie in args])
        return out_serie

    def setup_metadata_information(self, meta):
        """Set up standard metadata formats that later is writable.

        Args:
             meta: Contains pd.DataFrame(s) of metadata delivered to datahost
                   in excel spreadsheets [Metadata, Sensorinfo, Information]
        """
        # TODO should be able to handle multiple metadatasets? (.xlsx delivery files)
        self.delimiters = self._get_delimiters()
        self.df_metadata = self._get_reduced_dataframe(meta[0]['Metadata'])
        self.delivery_note = self._get_delivery_note(meta[0]['Förklaring'])
        self.template_format = self._get_template_format()
        self.df_sensorinfo = self._get_reduced_dataframe(meta[0]['Sensorinfo'])
        self.sensorinfo = self._get_sensorinfo_serie(separator=self.writer['separator_metadata'])
        self.information = self._get_information_serie(meta[0]['Information'],
                                                       separator=self.writer['separator_metadata'])
        self._adjust_data_formats()
        self._add_new_information_to_metadata()

    def _get_template_format(self):
        """Get standard format of template output."""
        # TODO adjust reader, get format from tamplate ('Förklaring').. ö..
        return pd.Series([''.join([self.writer['prefix_format'],
                                   '=', self.delivery_note['DTYPE']])])

    def _get_delimiters(self):
        """Return delimiters of data and meta."""
        # FIXME Redo and delete hardcoded parts.. Get better solution than '\ t'.replace(' ','') for tabb-sign
        # FIXME self.writer['separator_data']])}
        return {'meta': pd.Series([''.join([self.writer['prefix_metadata_delimiter'],
                                            '=', self.writer['separator_metadata']])]),
                'data': pd.Series([''.join([self.writer['prefix_data_delimiter'],
                                            '=', '\ t'.replace(' ', '')])])}  # noqa: W605

    def _get_delivery_note(self, delivery_info):
        """Return dictionary with information taken from the delivery_note ("Förklarings-flik")"""
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
        """Return numpy.array containing indices.

        Args:
            df (pd.DataFrame): data
            check_values (list): Checklist in order of importance

        Returns:
            (array([15], dtype=int64), array([0], dtype=int64))
        """
        for value in check_values:
            if any(df == value):
                return utils.get_index_where_df_equals_x(df, value)
        return None

    def extract_metadata(self, filename, separator=None):
        """Return pandas.Serie with metadata according to template standards.

        Takes columns from dataframe and merges with dataframe values together with a seperator.
        Example of one pd.Serie value: '//METADATA;SDATE;2020-08-25'

         Args:
            filename (str): filename of raw data
            separator (str): separator to separate row values
        """
        meta = self.extract_metadata_dataframe(filename)
        self.reset_index(meta)
        meta = meta.iloc[0].to_list()
        serie = pd.Series(self.df_metadata.columns)

        serie = serie.str.cat(meta, sep=separator)
        serie = serie.radd(self.writer['prefix_metadata'] + separator)

        return serie

    def extract_metadata_dataframe(self, filename):
        """Return one row from self.df_metadata (pd.DataFrame)."""
        boolean = self.get_index(self.file_name, filename.upper(),
                                 equals=True, as_boolean=True)
        return self.df_metadata.loc[boolean, :]

    @staticmethod
    def _get_reduced_dataframe(df):
        """Exclude empty column "Tabellhuvud:"."""
        if 'Tabellhuvud:' in df:
            df.pop('Tabellhuvud:')
        return df

    def _get_sensorinfo_serie(self, separator=None):
        """Get dictionary with sensorinfo.

        Args:
            separator (str): separator to separate row values
        """
        out_info = {}
        for inst_serno in self.df_sensorinfo['INSTRUMENT_SERIE'].unique():
            out_info[inst_serno] = [pd.Series(self.df_sensorinfo.columns).str.cat(sep=separator)]

        for _, row in self.df_sensorinfo.iterrows():
            out_info[row['INSTRUMENT_SERIE']].append(row.str.cat(sep=separator))

        for inst_serno in out_info.keys():
            out_info[inst_serno] = self.get_series_object(out_info[inst_serno])
            out_info[inst_serno] = out_info[inst_serno].radd(self.writer['prefix_sensorinfo'] + separator)
        return out_info

    def _get_information_serie(self, info, separator=None):
        """Get list with "other" information.

        Args:
            separator (str): separator to separate row values
        """
        # TODO is it ok that the information sheet is assumed to be a single column?
        out_info = [pd.Series(info.columns).str.cat(sep=separator)]
        for _, row in info.iterrows():
            out_info.append(row.str.cat(sep=separator))

        out_info = self.get_series_object(out_info)
        out_info = out_info.radd(self.writer['prefix_info'] + separator)
        return out_info

    def _get_instrument_metadata(self, serie, separator=None, data_identifier=None):
        """Get pd.serie with instrument metadata.

        Sorts out instrument metadata from serie (everything but data).

        Args:
            serie: Data in raw format
            separator: separator to separate row values
            data_identifier: identifier of data within pandas.Series

        Returns:
            Lists according to template standards
        """
        if not data_identifier:
            data_identifier = self.writer['identifier_instrument_metadata_end']
        end_idx = self.get_index(serie, data_identifier)
        out_info = serie.iloc[:end_idx[0]]
        out_info = out_info.radd(self.writer['prefix_instrument_metadata'] + separator)
        return out_info

    def _get_data_serie(self, df, separator=None):
        """Return pd.Serie from dataframe.

        Args:
            df: data
            separator (str): separator to separate row values
        """
        out_info = [separator.join(df.columns)]
        out_info.extend(df.apply(lambda x: separator.join(x), axis=1).to_list())
        out_info = self.get_series_object(out_info)
        return out_info

    def _get_data_columns(self, data, metadata):
        """Rename columns of dataframe.

        Merge column data with extended metadata (multiply selected metadata fields to "data"-column length).

        Args:
            data: pd.DataFrame, Hi resolution
            metadata: 1 row pd.DataFrame
        """
        header = self.set_header()
        # if 'DEPH' not in header:
        #     header.append('DEPH')
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
        """Get column mapper.

        Creates dictionary with column name as key and new column name as value.
        """
        mapp_dict = {}
        for para, unit in zip(self.df_sensorinfo.PARAM, self.df_sensorinfo.MUNIT):
            wrapped_unit = ''.join(['[', unit, ']'])
            mapp_dict[para] = ' '.join([para, wrapped_unit])

        return mapp_dict

    def set_header(self):
        """Return complete header for CTD standard format.

        Adds specified parameters from sensorinfo (Excel spreadsheet) to the standard "Visit info header".
        """
        parameters_list = self.get_parameters_from_sensorinfo()
        return self.writer['standard_data_header'] + parameters_list

    def get_parameters_from_sensorinfo(self, qc0=True):
        """Return all parameters from sensorinfo including Q-flags.

        Args:
            qc0 (bool): True / False. If flag "QC-0" should be included.
        """
        # TODO qc0.. if QC-0 has been performed we have a True value
        outlist = []
        for param in self.df_sensorinfo.loc[self.sensorinfo_boolean, 'PARAM'].values:
            outlist.append(param)
            if qc0:
                outlist.append('Q0_' + param)
            outlist.append('Q_' + param)
        return outlist

    def _get_writer_settings(self):
        """Get writer settings"""
        return self.settings.writers['ctd_standard_template']['writer']

    @staticmethod
    def get_metadata_sets(datasets):
        """Get metadata sets."""
        # TODO presumably we might need to handle other metadata formats than xlsx?
        out_sets = []
        for dset in datasets:
            for key in dset:
                if key.endswith('.xlsx'):
                    out_sets.append(dset[key])
        return out_sets

    @staticmethod
    def get_datasets(datasets):
        """Get datasets (not metadata files)."""
        out_sets = []
        for dset in datasets:
            for key in dset:
                if not key.endswith('.xlsx'):
                    out_sets.append(dset)
                    break
        return out_sets

    def _get_save_path(self, fid):
        """Get filename path."""
        if not hasattr(self, 'data_path'):
            self._set_data_path()
            utils.check_path(self.data_path)

        if 'delivery_note' in fid or 'metadata' in fid or 'sensorinfo' in fid or 'information' in fid:
            pass
        elif not fid.startswith(self.writer.get('filename')):
            fid = self._replace_data_file_name(fid)

        file_path = ''.join((fid.split('.')[0], self.writer.get('extension_filename')))
        file_path = os.path.join(self.data_path, file_path)
        return file_path

    def _replace_data_file_name(self, fid):
        """Return FILE_NAME_DATABASE."""
        boolean = self.file_name == fid.upper()
        return self.df_metadata.loc[boolean, 'FILE_NAME_DATABASE'].values[0]

    def _set_data_path(self):
        """Set path to data file."""
        folder_prefix = 'ctd_std_fmt_' + utils.get_datetime_now(fmt='%Y%m%d_%H%M%S')
        self.data_path = os.path.join(self.settings.settings_paths.get('export_path'), folder_prefix)

    def _update_visit_info(self, metadata):
        """Update visit info properties of parent class."""
        self._update_visit_datetime_object(metadata)
        self._update_visit_position(metadata)
        self._update_visit_cruise_name(metadata)
        self._update_visit_station(metadata)

    def _update_visit_cruise_name(self, metadata):
        """Update cruise property of BaseFileHandler."""
        shipc = metadata.at[0, 'SHIPC']
        cruise_no = metadata.at[0, 'CRUISE_NO']
        self.update_cruise(shipc, cruise_no)

    def _update_visit_datetime_object(self, metadata):
        """Update visit date/time properties of BaseFileHandler."""
        sdate = metadata.at[0, 'SDATE']
        stime = metadata.at[0, 'STIME']
        self.update_datetime_object(sdate, stime)

    def _update_visit_position(self, metadata):
        """Update visit latitude/longitude properties of BaseFileHandler."""
        lat = metadata.at[0, 'LATIT']
        lon = metadata.at[0, 'LONGI']
        self.update_position(lat, lon)

    def _update_visit_station(self, metadata):
        """Update station property of BaseFileHandler."""
        statn = metadata.at[0, 'STATN']
        self.update_station_name(statn)

    @property
    def file_name(self):
        """Return file name"""
        return self._file_name

    @file_name.setter
    def file_name(self, file_series):
        """Set the file_name property."""
        self._file_name = file_series.str.upper()

    @property
    def sensorinfo_boolean(self):
        """Return sensorinfo boolean."""
        return self._sensorinfo_boolean

    @sensorinfo_boolean.setter
    def sensorinfo_boolean(self, value):
        """Set the sensorinfo_boolean property."""
        self._sensorinfo_boolean = self.df_sensorinfo['INSTRUMENT_SERIE'] == value

    def _check_dataset_format(self, datasets):
        """Check dataset format."""
        if len(datasets) == 1:
            self.std_format = True

    def _redirect_to_data_update(self, datasets):
        """Update data that is allready in the standard CTD-format.

        Args:
            datasets: Consits of data as CTD standard format. Each dataset has metadata according to standard format
                      (pd.Series) and data as pd.DataFrame datasets consists of CTD standard format. Each dataset has
                      metadata according to standard format (pd.Series) and data as pd.DataFrame.
        """
        sep = self.writer['separator_data']
        for key, item in datasets[0].items():
            # if 'data' in item.keys():
            #     data_series = self._get_data_serie(item['data'], separator=sep)
            # else:
            #     data_series = self._get_data_serie(item['hires_data'], separator=sep)
            data_series = self._get_data_serie(item['data'], separator=sep)
            data_series = self._append_information(item['metadata'],
                                                   data_series)
            self._write(key, data_series)
