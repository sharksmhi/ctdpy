# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 13:38:35 2018

@author: a002028
"""

# from core.writers.with_style import with_style


class XlsxWriter(object):
    """ """
    def __init__(self, with_style=False, in_template=None):
        self.with_style = with_style
        self.in_template = in_template

    def write(self, df, save_path, sheet_name='Data', na_rep='', index=False,  encoding='cp1252'):
        """
        :param df: pd.DataFrame
        :param save_path: str
        :param sheet_name: str
        :param na_rep: str, np.nan, None
        :param index: False or True
        :param encoding: str
        :return: Saved excel file
        """
        df.to_excel(save_path,
                    na_rep=na_rep,
                    sheet_name=sheet_name,
                    index=index,
                    encoding=encoding)

    @staticmethod
    def write_dataframe(df, save_path, sheet_name='Data', na_rep='', index=False,  encoding='cp1252'):
        """
        :param df: pd.DataFrame
        :param save_path: str
        :param sheet_name: str
        :param na_rep: str, np.nan, None
        :param index: False or True
        :param encoding: str
        :return: Saved excel file
        """
        df.to_excel(save_path,
                    na_rep=na_rep,
                    sheet_name=sheet_name,
                    index=index,
                    encoding=encoding)

















