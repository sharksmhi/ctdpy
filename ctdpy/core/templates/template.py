# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 12:09:23 2018

@author: a002028
"""
import pandas as pd
from ctdpy.core import utils


class TemplateBase(dict):
    """Base Class for template handlers."""

    def __init__(self):
        """Initialize."""
        super().__init__()

    def read(self, *args, **kwargs):
        """Read template."""
        raise NotImplementedError


class Template(pd.DataFrame):
    """Template Handler.

    Uses pandas DataFrame as subclass
    """

    @property
    def _constructor(self):
        """Constructor for Template"""
        return Template

    def check_data(self, data):
        """Return pd.DataFrame with columns that exists in self."""
        only_keys = [key for key in data if key in self.keys()]
        return data[only_keys]

    def convert_formats(self, ship_map=None):
        """Converts formats."""
        # FIXME Test version.. Use methods outside Template instead..
        if 'timestamp' in self:
            self['timestamp']
            self['MYEAR'] = self['timestamp'].apply(lambda x: utils.get_format_from_datetime_obj(x, '%Y'))
            self['STIME'] = self['timestamp'].apply(lambda x: utils.get_format_from_datetime_obj(x, '%H:%M'))
            self['SDATE'] = self['timestamp'].apply(lambda x: utils.get_format_from_datetime_obj(x, '%Y-%m-%d'))
        elif 'SDATE' in self:
            self['MYEAR'] = self['SDATE'].apply(lambda x: x[:4])

        self['LATIT'] = self['LATIT'].apply(lambda x: utils.strip_text(x, ['N', ' ']))
        self['LONGI'] = self['LONGI'].apply(lambda x: utils.strip_text(x, ['E', ' ']))

        try:
            self['SHIPC'] = self['SHIPC'].apply(lambda x: ship_map.map_shipc(x))
        except:
            self['SHIPC'] = '77SE'

    def import_column_order(self, order):
        """Set order of columns."""
        self.column_order = order

    def export_data_as_excel(self, with_style=False, columns=None, save_path='', sheet_name='Data'):
        """Write data to excel file.

        Args:
            with_style (bool): False or True, implements StyleSheet
                               instead of ordinary pd.DataFrame
            columns (list): Columns to write
            save_path (str): Path to file
            sheet_name (str): Name of sheet
        """
        # FIXME Use writer instead!
        if with_style:
            pass
            # self._save_with_style()
        else:
            self.to_excel(save_path,
                          sheet_name=sheet_name,
                          na_rep='',
                          columns=columns,
                          index=False,
                          encoding='cp1252')

    def import_metadata(self, meta, len_col=None):
        """Append metadata to template (self)."""
        if isinstance(meta, dict):
            meta = pd.DataFrame([meta]*len_col)
        elif isinstance(meta, pd.core.frame.DataFrame):
            meta = pd.concat([meta]*len_col, ignore_index=True)
        else:
            raise TypeError(type(meta) + ' is not supported by this import function')

        self = self.append(meta, ignore_index=True)

    def sort(self, sort_by_keys=None):
        """Sort dataframe by "sort_by_keys"."""
        sort_by_keys = sort_by_keys or []
        self.sort_values(sort_by_keys, ascending=[True]*len(sort_by_keys), inplace=True)
        self.reset_index(drop=True, inplace=True)
