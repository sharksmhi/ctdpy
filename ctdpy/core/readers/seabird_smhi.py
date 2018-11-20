# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 09:37:38 2018

@author: a002028
"""
#
#
""" Sea-Bird reader
"""
import sys
sys.path.append("..")
import config
from core.utils import get_filename
from core.data_handlers import DataFrameHandler
from core.data_handlers import SeriesHandler
from core.data_handlers import BaseReader
from core.readers.cnv_reader import CNVreader
from core import ctd_profile
from core.readers.xlsx_reader import load_excel

"""
#==============================================================================
#==============================================================================
"""


class SeaBirdSMHI(BaseReader, CNVreader, SeriesHandler):
    # FIXME come on.. new name!
    """
    """
    def __init__(self, settings):
        super().__init__(settings)
        self.df_handler = DataFrameHandler(self.settings)

    def get_data(self, filenames=None, add_low_resolution_data=False):
        """
        :param filenames: list of file paths
        :param merge_data_and_metadata: False or True
        :param add_low_resolution_data: False or True
        :return: datasets
        """
        data = {}
        if add_low_resolution_data:
            profile = ctd_profile.CtdProfile()

        for fid in filenames:
            file_data = self.load(fid)
            fid = get_filename(fid)
            self._setup_dictionary(fid, data)

            serie = self.get_series_object(file_data)
            hires_data = self._setup_dataframe(serie)

            data[fid]['raw_format'] = serie
            data[fid]['metadata'] = self.get_metadata(serie)
            data[fid]['hires_data'] = hires_data

            if add_low_resolution_data:
                profile.update_data(data=hires_data)
                lores_data = profile.extract_lores_data(key_depth='DEPH',
                                                        discrete_depths=self.settings.depths)
                data[fid]['lores_data'] = lores_data

        return data

    def get_metadata(self, serie, map_keys=True):
        """
        :param serie: pd.Series
        :param map_keys: False or True
        :return: Dictionary with metadata
        """
        meta_dict = {}
        for ident, sep in zip(['identifier_metadata', 'identifier_metadata_2'],
                              ['separator_metadata', 'separator_metadata_2']):
            data = self.get_meta_dict(serie, 
                                      identifier=self.settings.datasets['cnv'].get(ident), 
                                      separator=self.settings.datasets['cnv'].get(sep),
                                      keys=self.settings.datasets['cnv'].get('keys_metadata'))
            
            meta_dict = config.recursive_dict_update(meta_dict, data)
            
        if map_keys:
            meta_dict = {self.settings.pmap.get(key): meta_dict[key] for key in meta_dict}
            
        return meta_dict

    def merge_data(self, data, resolution='lores_data'):
        """
        :param data: Dictionary of specified dataset
        :param resolution: str
        :return: Updates data (dictionary with pd.DataFrames)
        """
        for fid in data:
            in_data = data[fid][resolution]
            in_data = self.df_handler.add_metadata_to_frame(in_data,
                                                            data[fid]['metadata'],
                                                            len_col=len(data[fid][resolution].index))
            data[fid][resolution+'_all'] = in_data

    def _setup_dataframe(self, serie):
        """
        :param serie: pd.Series
        :return: pd.DataFrame
        """
        header = self.get_data_header(serie, dataset='cnv')
        df = self.get_data_in_frame(serie, header, dataset='cnv')
        df = self.df_handler.map_column_names_of_dataframe(df)
        
        return df

    def _setup_dictionary(self, fid, data):
        """
        :param fid: str, file name identifier
        :return: standard dictionary structure
        """
        data[fid] = {'hires_data': None,
                     'lores_data': None,
                     'metadata': None}


"""
#==============================================================================
#==============================================================================
"""


class MetadataSMHI(BaseReader, DataFrameHandler):
    """
    """
    def __init__(self, settings):
        super().__init__(settings)
        self.data = {}

    def get_data(self, filenames=None, add_low_resolution_data=False):
        """
        :param filenames: list of file paths
        :return: Dictionary with DataFrames
        """
        reader = self.get_reader_instance()
        file_specs = self.settings.readers['seabird_smhi']['datasets']['xlsx']
        for file_path in filenames:
            fid = get_filename(file_path)
            self.data[fid] = {}
            self._read(file_path, file_specs, reader, self.data[fid])

        return self.data

    def merge_data(self, data, resolution=None):
        """
        :param data: data
        :param resolution: None
        :return: pass
        """
        pass

    @staticmethod
    def _read(file_path, file_specs, reader, data):
        """
        :param file_path: str
        :param file_specs: Dictionary
        :param reader: Reader instance
        :param data: Dictionary
        :return: Updates data
        """
        for sheet_name, header_row in zip(file_specs['sheet_names'], file_specs['header_rows']):
            df = reader(f_name=file_path,
                        sheet_name=sheet_name,
                        header_row=header_row)
            data[sheet_name] = df.fillna('')

    @staticmethod
    def get_reader_instance():
        """
        Could be done differently
        :return: Reader instance
        """
        return load_excel

