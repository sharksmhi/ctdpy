# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 12:09:23 2018

@author: a002028
"""
import pandas as pd
from ctdpy.core import utils


class TemplateBase(dict):
    """
    """
    def __init__(self):
        super().__init__()

    def read(self):#, reader):
        """

        :param reader:
        :return:
        """
        raise NotImplementedError


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

    def convert_formats(self, ship_map=None):
        """
        Converts formats
        :return: Converted formats
        """
        #FIXME Test version.. Use methods outside Template instead..
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
        """
        :param order: list
        :return:list
        """
        self.column_order = order

    def export_data_as_excel(self, with_style=False, columns=None,
                             save_path='', sheet_name='Data'):
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

    def sort(self, sort_by_keys=None):
        """
        :param sort_by_keys:
        :param df:
        :return:
        """
        sort_by_keys = sort_by_keys or []
        self.sort_values(sort_by_keys, ascending=[True]*len(sort_by_keys), inplace=True)
        self.reset_index(drop=True, inplace=True)


# class TemplateFrame(pd.DataFrame):
#     """
#     Uses pandas DataFrame as subclass
#     """
#     @property
#     def _constructor(self):
#         """
#         Constructor for TemplateFrame
#         :return: TemplateFrame
#         """
#         return TemplateFrame
#
#     def check_data(self, data):
#         """
#         :param data: pd.DataFrame
#         :return: pd.DataFrame with columns that exists in self (self is Template DataFrame)
#         """
#         only_keys = [key for key in data if key in self.keys()]
#         return data[only_keys]
#
#     def convert_formats(self, ship_map=None):
#         """
#         Converts formats
#         :return: Converted formats
#         """
#         #FIXME Test version.. Use methods outside Template instead..
#         self['datetime_format'] = self['SDATE'].apply(lambda x: utils.convert_string_to_datetime_obj(x, '%b %d %Y %H:%M:%S'))
#         self['STIME'] = self['datetime_format'].apply(lambda x: utils.get_format_from_datetime_obj(x, '%H:%M'))
#         self['SDATE'] = self['datetime_format'].apply(lambda x: utils.get_format_from_datetime_obj(x, '%Y-%m-%d'))
#         self['MYEAR'] = self['datetime_format'].apply(lambda x: utils.get_format_from_datetime_obj(x, '%Y'))
#         self['LATIT'] = self['LATIT'].apply(lambda x: utils.strip_text(x, ['N', ' ']))
#         self['LONGI'] = self['LONGI'].apply(lambda x: utils.strip_text(x, ['E', ' ']))
#
#         self['SHIPC'] = self['SHIPC'].apply(lambda x: ship_map.map_shipc(x))
#
#     def import_column_order(self, order):
#         """
#         :param order: list
#         :return:list
#         """
#         self.column_order = order
#
#     def export_data_as_excel(self, with_style=False, columns=None,
#                              save_path='', sheet_name='Data'):
#         """
#         :param with_style: False or True, implements StyleSheet instead of ordinary pd.DataFrame
#         :param columns: list, columns to write
#         :param save_path: str
#         :param sheet_name: str
#         :return: Saved excel file
#         """
#         # FIXME Use writer instead!
#         if with_style:
#             pass
# #            self._save_with_style()
#         else:
#             self.to_excel(save_path,
#                           sheet_name=sheet_name,
#                           na_rep='',
#                           columns=columns,
#                           index=False,
#                           encoding='cp1252')
#
#     def import_metadata(self, meta, len_col=None):
#         """
#         Append metadata to template (self)
#         :param meta: Dictionary, pd.DataFrame
#         :param len_col: int
#         :return: Appended pd.DataFrame
#         """
#         if isinstance(meta, dict):
#             meta = pd.DataFrame([meta]*len_col)
#         elif isinstance(meta, pd.core.frame.DataFrame):
#             meta = pd.concat([meta]*len_col, ignore_index=True)
#         else:
#             raise TypeError(type(meta) + ' is not supported by this import \
#             function')
#
#         self = self.append(meta, ignore_index=True)
