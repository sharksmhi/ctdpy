# -*- coding: utf-8 -*-
"""
Created on 2019-12-11 15:28

@author: a002028
"""
from ctdpy.core import utils
from ctdpy.core.profile import Profile
# from ctdpy.core.calculator import Calculator
from ctdpy.core.data_handlers import DataFrameHandler
from ctdpy.core.data_handlers import SeriesHandler
from ctdpy.core.data_handlers import BaseReader
from ctdpy.core.readers.cnv_reader import CNVreader


class Rinco(BaseReader, CNVreader, SeriesHandler):
    """Reader for rinco data."""

    ts_map = {'YEAR': 'year',
              'MONTH': 'month',
              'DAY': 'day',
              'HOUR': 'hour',
              'MINUTE': 'minute',
              'SECOND': 'second'}

    def __init__(self, settings):
        """Initialize."""
        super().__init__(settings)
        self.df_handler = DataFrameHandler(self.settings)

    def add_calculated_parameters(self, df, latit):
        """Calculate parameters and add them to the dataframe."""
        # if 'DEPH' not in df:
        #     calc = Calculator()
        #     df['DEPH'] = calc.get_true_depth(
        #         attribute_dictionary={
        #             'latitude': latit,
        #             'pressure': df['PRES_CTD'].astype(np.float),
        #             'gravity': df['PRES_CTD'].astype(np.float),
        #             'density': df['DENS_CTD'].astype(np.float)
        #         }
        #     )
        #     self.metadata_update.setdefault('DEPH': )

        timestamp_array = df[['SDATE', 'STIME']].apply(
            lambda x: utils.get_timestamp(' '.join(x)), axis=1)
        for ts_key in self.ts_map:
            df[ts_key] = timestamp_array.dt.__getattribute__(
                self.ts_map.get(ts_key)).astype(str)
            df[ts_key] = df[ts_key].str.zfill(2)

    def get_data(self, filenames=None, add_low_resolution_data=False):
        """Get data and metadata.

        Args:
            filenames (iterable): A sequence of files that will be used to
                                  load data from.
            add_low_resolution_data: False | True
        """
        data = {}
        if add_low_resolution_data:
            profile = Profile()

        for fid in filenames:
            file_data = self.load(fid)
            fid = utils.get_filename(fid)
            self.setup_dictionary(fid, data)

            serie = self.get_series_object(file_data)
            hires_data = self.setup_dataframe(serie, metadata=None)
            metadata = self.get_metadata(
                serie,
                filename=fid,
                sdate=hires_data['SDATE'][0],
                stime=hires_data['STIME'][0],
            )

            data[fid]['raw_format'] = serie
            data[fid]['metadata'] = metadata
            data[fid]['data'] = hires_data
            data[fid]['identifier_data'] = self.settings.datasets['tob'][
                'identifier_data']

            if add_low_resolution_data:
                profile.update_data(data=hires_data)
                lores_data = profile.extract_lores_data(
                    key_depth='DEPH',
                    discrete_depths=self.settings.depths
                )
                data[fid]['lores_data'] = lores_data
        return data

    def get_metadata(self, serie, map_keys=True, filename=None,
                     sdate=None, stime=None):
        """Dummie method."""
        raise NotImplementedError

    def merge_data(self, data, resolution='lores_data'):
        """Merge data with metadata.

        Args:
            data (dict): Dictionary of specified dataset
            resolution (str): key for resolution
        """
        for fid in data:
            in_data = data[fid][resolution]
            in_data = self.df_handler.add_metadata_to_frame(
                in_data,
                data[fid]['metadata'],
                len_col=len(data[fid][resolution].index)
            )
            data[fid][resolution + '_all'] = in_data

    def setup_dataframe(self, serie, metadata=None):
        """Convert pandas Serie into pandas DataFrame."""
        header = self.get_data_header(serie, dataset='tob', first_row=True)
        if header[0] == ';':
            header.remove(';')
        df = self.get_data_in_frame(serie, header, dataset='tob')
        df = self.df_handler.map_column_names_of_dataframe(df)

        self.add_calculated_parameters(df, latit=59.)  # metadata['LATIT'])

        return df

    def setup_dictionary(self, fid, data, keys=None):
        """Set standard dictionary structure."""
        keys = keys or ['data', 'lores_data', 'metadata']
        data[fid] = {key: None for key in keys}
