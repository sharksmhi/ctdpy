# -*- coding: utf-8 -*-
"""
Created on 2020-02-18 13:23

@author: a002028

"""
from ctdpy.core import utils
from ctdpy.core.data_handlers import DataFrameHandler
from ctdpy.core.data_handlers import SeriesHandler
from ctdpy.core.data_handlers import BaseReader
from ctdpy.core.readers.cnv_reader import CNVreader
from ctdpy.core.profile import Profile


class MVP200(BaseReader, CNVreader, SeriesHandler):
    """MVP-reader (Moving Vessel Profiler)"""
    def __init__(self, settings):
        super().__init__(settings)
        self.df_handler = DataFrameHandler(self.settings)

    def get_data(self, filenames=None, add_low_resolution_data=False):
        """Get data and metadata.

        Args:
            filenames (iterable): A sequence of files that will be used to load data from.
            add_low_resolution_data: False | True
        """
        data = {}
        profile = Profile() if add_low_resolution_data else None

        for fid in filenames:
            file_data = self.load(fid)
            fid = utils.get_filename(fid)
            self.setup_dictionary(fid, data)

            serie = self.get_series_object(file_data)
            metadata = self.get_metadata(serie, filename=fid)
            hires_data = self.setup_dataframe(serie, metadata=metadata)

            data[fid]['raw_format'] = serie
            data[fid]['metadata'] = metadata
            data[fid]['data'] = hires_data

            if add_low_resolution_data:
                profile.update_data(data=hires_data)
                lores_data = profile.extract_lores_data(key_depth='DEPH',
                                                        discrete_depths=self.settings.depths)
                data[fid]['lores_data'] = lores_data

        return data

    def get_metadata(self, serie, map_keys=True, filename=None):
        """Return dictionary with metadata."""
        meta_dict = {}
        for ident, sep in zip(['identifier_metadata', 'identifier_metadata_2'],
                              ['separator_metadata', 'separator_metadata_2']):
            data = self.get_meta_dict(serie,
                                      identifier=self.settings.datasets['cnv'].get(ident),
                                      separator=self.settings.datasets['cnv'].get(sep),
                                      keys=self.settings.datasets['cnv'].get('keys_metadata'))

            meta_dict = utils.recursive_dict_update(meta_dict, data)

        if map_keys:
            meta_dict = {self.settings.pmap.get(key): meta_dict[key] for key in meta_dict}

        return meta_dict

    def merge_data(self, data, resolution='lores_data'):
        """Merge data with metadata.

        Args:
            data (dict): Dictionary of specified dataset
            resolution (str): key for resolution
        """
        for fid in data:
            in_data = data[fid][resolution]
            in_data = self.df_handler.add_metadata_to_frame(in_data,
                                                            data[fid]['metadata'],
                                                            len_col=len(data[fid][resolution].index))
            data[fid][resolution + '_all'] = in_data

    def setup_dataframe(self, serie, metadata=None):
        """Convert pandas Serie into pandas DataFrame."""
        header = self.get_data_header(serie, dataset='cnv')
        df = self.get_data_in_frame(serie, header, dataset='cnv')
        df = self.df_handler.map_column_names_of_dataframe(df)

        return df

    def setup_dictionary(self, fid, data, keys=None):
        """Setup standard dictionary structure."""
        keys = keys or ['data', 'lores_data', 'metadata']
        data[fid] = {key: None for key in keys}
