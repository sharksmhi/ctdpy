# -*- coding: utf-8 -*-
"""
Created on 2018-11-20 08:55

@author: Johannes Johansson

"""
from ctdpy.core import utils
from ctdpy.core.data_handlers import DataFrameHandler
from ctdpy.core.data_handlers import SeriesHandler
from ctdpy.core.writers.xlsx_writer import XlsxWriter


class MetadataWriter(SeriesHandler, DataFrameHandler):
    """Convert datasets into standard output for CTD metadata (Xlsx Writer)."""

    def __init__(self, settings):
        """Load writer and initialize the template handler."""
        super().__init__(settings)
        self.writer = self._get_writer_settings()
        self.xlsx_writer = XlsxWriter()
        # self.template = None
        # self.load_template()
        handler_instance = self.get_handler_instance()
        self.template_handler = handler_instance(self.settings)

    # def load_template(self):
    #     """
    #     :return: Loads Template Handler
    #     """
    #     handler_instance = self.get_handler_instance()
    #     self.template_handler = handler_instance(self.settings)

    def get_handler_instance(self):
        """Return Template Handler."""
        return self.settings.templates['ctd_metadata'].get('template_handler')

    def convert_formats(self):
        """Call the convert_formats method of the current template handler."""
        self.template_handler.template['Metadata'].convert_formats(ship_map=self.settings.smap)

    def write(self, dataset):
        """Write dataset to file."""
        for fid, item in dataset.items():
            item['metadata']['FILE_NAME'] = fid
            self.append_to_template(item['metadata'])

        self.convert_formats()
        self.template_handler.template['Metadata'].sort(sort_by_keys=['SHIPC', 'SDATE', 'STIME'])
        self._write()

    def _write(self):
        """Write to file."""
        save_path = self._get_save_path()
        headers = [True if h is not None else None for h in self.settings.templates['ctd_metadata'][
            'template']['header_row']]
        start_rows = [h if h is not None else 0 for h in self.settings.templates['ctd_metadata'][
            'template']['header_row']]
        self.xlsx_writer.write_multiple_sheets(save_path,
                                               dict_df=self.template_handler.template,
                                               sheet_names=self.settings.templates['ctd_metadata']['template'][
                                                   'sheet_name'],
                                               headers=headers,
                                               start_rows=start_rows)
        self.data_path = save_path

    def append_to_template(self, df):
        """Append the given dataframe to the template handler."""
        self.template_handler.append_to_template(df, template_key='Metadata')

    def _get_data_path(self):
        """Return path to data."""
        time_now = utils.get_datetime_now(fmt='%Y%m%d_%H%M%S')
        return ''.join([self.settings.settings_paths.get('export_path'),
                        'metadata_', time_now, '/'])

    def _get_save_path(self):
        """Return path to file."""
        data_path = self._get_data_path()
        utils.check_path(data_path)
        save_path = ''.join([data_path, self.writer.get('filename'),
                             self.writer.get('extension_filename')])
        return save_path

    def _get_writer_settings(self):
        """Return writer settings."""
        return self.settings.writers['metadata_template']['writer']
