# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 17:06:23 2018

@author: a002028
"""

from ctdpy.core.data_handlers import DataFrameHandler
from ctdpy.core.templates.template import Template


class PhyCheTemplateHandler(DataFrameHandler):
    """
    Uses DataFrameHandler as Base
    """
    def __init__(self, settings):
        super().__init__(settings)
        # self.settings = settings
        self.template = self.load_template()

    def append_to_template(self, data):
        """
        :param data: pd.DataFrame
        :return: appends data to template
        """
        data = self.template.check_data(data)
        self.template = self.template.append(data, ignore_index=True, sort=False)

    def convert_formats(self):
        """
        Convert formats of specified parameters (see core.templates.template.Template)
        :return:
        """
        self.template.convert_formats()

    def load_template(self):
        """
        Load standard template
        :return:
        """
        reader = self.get_reader()
        #TODO **kwargs
        empty_template = reader(self.settings.templates['phyche']['template'].get('file_path'),
                                sheet_name=self.settings.templates['phyche']['template'].get('data_sheetname'),
                                header_row=self.settings.templates['phyche']['template'].get('header_row'))

        return Template(empty_template)

    def get_template_columns(self):
        """
        :return: list of template primary columns
        """
        #FIXME Needed? we have .get_data_header(df) in baseclass but not as list...
        return list(self.template.columns)

    def get_reader(self):
        """
        :return: Reader instance
        """
        return self.settings.templates['phyche']['template'].get('reader')

