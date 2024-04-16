# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 17:06:23 2018

@author: a002028
"""
from ctdpy.core.data_handlers import DataFrameHandler
from ctdpy.core.templates.template import Template


class PhyCheTemplateHandler(DataFrameHandler):
    """Excel template handler for physical and chemical data.

    Discrete depths.
    """

    def __init__(self, settings):
        """Initialize and load template."""
        super().__init__(settings)
        self.template = self.load_template()

    def append_to_template(self, data, meta=None):
        """Append data and metadata to template."""
        mapper = {key: self.settings.pmap.get(key) for key in data.columns}

        # ts = '{YEAR:4s}-{MONTH:2s}-{DAY:2s} {HOUR:2s}:{MINUTE:2s}:{SECOND:2s}'
        # data['timestamp'] = data[
        #     ['YEAR', 'MONTH', 'DAY', 'HOUR', 'MINUTE', 'SECOND']].apply(
        #     lambda x: pd.Timestamp(ts.format(**x)), axis=1
        # )
        # data['SDATE'] = data[['YEAR', 'MONTH', 'DAY']].apply(
        #     lambda x: '{YEAR:4s}-{MONTH:2s}-{DAY:2s}'.format(**x), axis=1
        # )
        # data['STIME'] = data[['HOUR', 'MINUTE']].apply(
        #     lambda x: '{HOUR:2s}:{MINUTE:2s}'.format(**x), axis=1
        # )
        data = self.template.check_data(data.rename(mapper, axis=1))

        if meta:
            for key, item in meta.items():
                if key in self.template:
                    data[key] = item

        self.template = self.template.append(
            data, ignore_index=True, sort=False
        )

    def convert_formats(self):
        """Convert formats of specified parameters.

        See core.templates.template.Template
        """
        self.template.convert_formats()

    def load_template(self):
        """Load standard template."""
        reader = self.get_reader()
        # TODO **kwargs
        empty_template = reader(
            self.settings.templates['phyche']['template'].get('file_path'),
            sheet_name=self.settings.templates['phyche']['template'].get(
                'data_sheetname'),
            header_row=self.settings.templates['phyche']['template'].get(
                'header_row')
        )

        return Template(empty_template)

    def get_template_columns(self):
        """Return list of template primary columns."""
        # FIXME Needed? we have .get_data_header(df)
        #  in baseclass but not as list...
        return list(self.template.columns)

    def get_reader(self):
        """Reader instance."""
        return self.settings.templates['phyche']['template'].get('reader')
