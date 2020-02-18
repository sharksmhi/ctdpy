# -*- coding: utf-8 -*-
"""
Created on 2018-11-29 07:54:27

@author: Johannes Johansson

"""

from ctdpy.core.data_handlers import DataFrameHandler
from ctdpy.core.templates.template import Template
from ctdpy.core import utils


class CTDTemplateHandler(DataFrameHandler):
    """
    Uses DataFrameHandler as Base
    """
    def __init__(self, settings):
        super().__init__(settings)
        self.template = self.read_template()
        self.template['Metadata'] = Template(self.template['Metadata'])

    def append_to_template(self, data, template_key=None):
        """
        :param data: pd.DataFrame
        :return: appends data to template
        """
        self.template[template_key] = self.template[template_key].append(data, ignore_index=True, sort=False)

    def read_template(self):
        """
        Load standard template
        :return:
        """
        reader = self.get_reader()
        kwargs = utils.get_kwargs(reader, self.settings.templates['ctd_metadata']['template'])
        return reader(**kwargs)

        # self.template = Template(empty_template)

    def get_template_columns(self, template_key=None):
        """
        :return: list of template primary columns
        """
        #FIXME Needed? we have .get_data_header(df) in baseclass but not as list...
        return list(self.template[template_key].columns)

    def get_reader(self):
        """
        :return: Reader instance
        """
        return self.settings.templates['ctd_metadata']['template'].get('reader')

