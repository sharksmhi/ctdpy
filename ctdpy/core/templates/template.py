# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 12:09:23 2018

@author: a002028
"""

import numpy as np
from core.readers.xlsx_reader import load_excel

import pandas as pd
from datetime import datetime
import re
"""
#=========================================================================
#=========================================================================
"""

class TemplateBase(dict):
    """

    """
    def __init__(self):
        pass

    def read(self):#, reader):
        """

        :param reader:
        :return:
        """
        raise NotImplementedError


class TemplateFrame(pd.DataFrame):
    """
    Uses pandas DataFrame as subclass 
    """
    @property
    def _constructor(self):
        """
        Constructor for TemplateFrame
        :return: TemplateFrame
        """
        return TemplateFrame

    def check_data(self, data):
        """
        :param data: pd.DataFrame
        :return: pd.DataFrame with columns that exists in self (self is Template DataFrame)
        """
        only_keys = [key for key in data if key in self.keys()]
        return data[only_keys]

    def convert_formats(self):
        """
        Converts formats
        :return: Converted formats
        """
        #FIXME Test version.. Use methods outside Template instead..
        self['datetime_format'] = self[u'SDATE'].apply(lambda x: datetime.strptime(x, '%b %d %Y %H:%M:%S'))
        self.STIME = self[u'datetime_format'].apply(lambda x: x.strftime('%H:%M'))
        self.SDATE = self[u'datetime_format'].apply(lambda x: x.strftime('%Y-%m-%d'))
        self.MYEAR = self[u'datetime_format'].apply(lambda x: x.strftime('%Y'))
        self.LATIT = self[u'LATIT'].apply(lambda x: re.sub('[N ]', '', x))
        self.LONGI = self[u'LONGI'].apply(lambda x: re.sub('[E ]', '', x))

    def import_column_order(self, order):
        """
        :param order: list
        :return:list
        """
        self.column_order = order

    def export_data_as_excel(self, with_style=False, columns=None,
                             save_path=u'', sheet_name='Data'):
        """
        :param with_style: False or True, implements StyleSheet instead of ordinary pd.DataFrame
        :param columns: list, columns to write
        :param save_path: str
        :param sheet_name: str
        :return: Saved excel file
        """
        # FIXME Use writer instead!
        if with_style:
            pass
#            self._save_with_style()
        else:
            self.to_excel(save_path,
                          sheet_name=sheet_name,
                          na_rep='',
                          columns=columns,
                          index=False,
                          encoding='cp1252')

    def import_metadata(self, meta, len_col=None):
        """
        Append metadata to template (self)
        :param meta: Dictionary, pd.DataFrame
        :param len_col: int
        :return: Appended pd.DataFrame
        """
        if isinstance(meta, dict):
            meta = pd.DataFrame([meta]*len_col)
        elif isinstance(meta, pd.core.frame.DataFrame):
            meta = pd.concat([meta]*len_col, ignore_index=True)
        else:
            raise TypeError(type(meta) + ' is not supported by this import \
            function')

        self = self.append(meta, ignore_index=True)


class Template(pd.DataFrame):
    """
    Uses pandas DataFrame as subclass
    """
    @property
    def _constructor(self):
        """
        Constructor for TemplateFrame
        :return: Template
        """
        return Template

    def check_data(self, data):
        """
        :param data: pd.DataFrame
        :return: pd.DataFrame with columns that exists in self (self is Template DataFrame)
        """
        only_keys = [key for key in data if key in self.keys()]
        return data[only_keys]

    def convert_formats(self):
        """
        Converts formats
        :return: Converted formats
        """
        #FIXME Test version.. Use methods outside Template instead..
        self['datetime_format'] = self[u'SDATE'].apply(lambda x: datetime.strptime(x, '%b %d %Y %H:%M:%S'))
        self.STIME = self[u'datetime_format'].apply(lambda x: x.strftime('%H:%M'))
        self.SDATE = self[u'datetime_format'].apply(lambda x: x.strftime('%Y-%m-%d'))
        self.MYEAR = self[u'datetime_format'].apply(lambda x: x.strftime('%Y'))
        self.LATIT = self[u'LATIT'].apply(lambda x: re.sub('[N ]', '', x))
        self.LONGI = self[u'LONGI'].apply(lambda x: re.sub('[E ]', '', x))

    def import_column_order(self, order):
        """
        :param order: list
        :return:list
        """
        self.column_order = order

    def export_data_as_excel(self, with_style=False, columns=None,
                             save_path=u'', sheet_name='Data'):
        """
        :param with_style: False or True, implements StyleSheet instead of ordinary pd.DataFrame
        :param columns: list, columns to write
        :param save_path: str
        :param sheet_name: str
        :return: Saved excel file
        """
        # FIXME Use writer instead!
        if with_style:
            pass
#            self._save_with_style()
        else:
            self.to_excel(save_path,
                          sheet_name=sheet_name,
                          na_rep='',
                          columns=columns,
                          index=False,
                          encoding='cp1252')

    def import_metadata(self, meta, len_col=None):
        """
        Append metadata to template (self)
        :param meta: Dictionary, pd.DataFrame
        :param len_col: int
        :return: Appended pd.DataFrame
        """
        if isinstance(meta, dict):
            meta = pd.DataFrame([meta]*len_col)
        elif isinstance(meta, pd.core.frame.DataFrame):
            meta = pd.concat([meta]*len_col, ignore_index=True)
        else:
            raise TypeError(type(meta) + ' is not supported by this import \
            function')

        self = self.append(meta, ignore_index=True)
