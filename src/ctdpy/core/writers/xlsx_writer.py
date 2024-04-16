# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 13:38:35 2018

@author: a002028
"""
import pandas as pd


class XlsxWriter:
    """Writer of text files."""

    def __init__(self, with_style=False, in_template=None):
        """Initialize and store in_template."""
        self.with_style = with_style
        self.in_template = in_template

        # TODO Is self.in_template ever used?
        # self._load_xlsx_writer()

    def _load_xlsx_writer(self, save_path, engine='openpyxl'):
        """Create a Pandas Excel writer using engine."""
        self.xlsx_writer = pd.ExcelWriter(save_path, engine=engine)

    def write_multiple_sheets(self, save_path, dict_df=None, sheet_names=None,
                              headers=None, start_rows=None, na_rep='',
                              index=False, encoding='cp1252'):
        """Write excel file with multiple sheets.

        Args:
            save_path (str): Full path to file
            dict_df (dict): Dictionary with multiple pd.DataFrame
            sheet_names (list): Sheet names
            headers (list): List of False or True
            start_rows (list): List of numbers for each sheet.
            na_rep: value for nan-values
            index (bool): False or True
            encoding (str): Encoding to use when writing
        """
        self._load_xlsx_writer(save_path)
        for sheet, head, st_row in zip(sheet_names, headers, start_rows):
            dict_df[sheet].to_excel(
                self.xlsx_writer,
                sheet_name=sheet,
                header=head,
                startrow=st_row,
                na_rep=na_rep,
                index=index,
                encoding=encoding
            )
        self.close_writer()

    def close_writer(self):
        """Close the Pandas Excel writer and save the Excel file."""
        self.xlsx_writer.save()

    @staticmethod
    def write(df, save_path, sheet_name='Data', na_rep='', index=False,
              encoding='cp1252', **kwargs):
        """Write dataframe to excel file."""
        df.to_excel(
            save_path,
            na_rep=na_rep,
            sheet_name=sheet_name,
            index=index,
            encoding=encoding
        )
