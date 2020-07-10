# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 10:50:49 2018

@author: a002028

"""
from ctdpy.core import config, data_handlers
from ctdpy.core.archive_handler import Archive
from ctdpy.core.utils import get_file_list_based_on_suffix, generate_filepaths, get_reversed_dictionary, match_filenames


class Session(object):
    """
    """
    def __init__(self, filepaths=None, reader=None):

        self.settings = config.Settings()
        self.update_settings_attributes(**self.settings.readers[reader])

        filepaths = list(filepaths)
        self.readers = self.create_reader_instances(filepaths=filepaths,
                                                    reader=reader)

    def _set_file_reader(self):
        """
        #FIXME do we use this one?
        :return:
        """
        self.file_reader = self.settings.reader

    def read(self, add_merged_data=False, add_low_resolution_data=False):
        """
        :param add_merged_data: False or True
        :param add_low_resolution_data: Include extra pd.DataFrame for low resolution data
        :return: list, datasets
        """
        datasets = self._read_datasets(add_merged_data, add_low_resolution_data)
        return datasets

    def _read_datasets(self, add_merged_data, add_low_resolution_data):
        """
        Different "datasets" for one type of data (e.g. seabird_smhi).
        Could be both cnv and xlsx files (metadata and data seperated
        in different files but belong together).
        :param add_merged_data: False or True
        :param add_low_resolution_data: Include extra pd.DataFrame for low resolution data
        :return:
        """
        #TODO Merge the different datasets?
        datasets = []
        for dataset in self.readers:
            print('dataset', dataset)
            data = self.readers[dataset]['reader'].get_data(filenames=self.readers[dataset]['file_names'],
                                                            add_low_resolution_data=add_low_resolution_data)

            # TODO add_merged_data will ONLY merge profile data with meta data into PHYCHE-template. we should therefore do this elsewhere
            if add_merged_data and add_low_resolution_data:
                # data = self.readers[dataset]['reader'].merge_data(data, resolution='lores_data')
                self.readers[dataset]['reader'].merge_data(data, resolution='lores_data')

            datasets.append(data)

        return datasets

    @staticmethod
    def _get_filenames_matched(filenames, file_type):
        """
        :param filenames: list of strings
        :param file_type: from reader **kwargs
        :return: list of matched filenames
        """
        if 'file_patterns' in file_type:
            filenames_matched = match_filenames(filenames, file_type['file_patterns'])
        elif 'file_suffix' in file_type:
            filenames_matched = get_file_list_based_on_suffix(filenames, file_type['file_suffix'])
        else:
            raise ImportWarning('No file_pattern nor suffix is readable in reader.file_types')
        return filenames_matched

    def create_reader_instances(self, filepaths=None, reader=None):
        """
        Find readers and return their instances
        :param filenames: list of strings
        :param reader: string
        :return: Dictionary, reader instances
        """
        #TODO Redo and move to utils.py or __init__.py
        reader_instances = {}
        for dataset, dictionary in self.settings.readers[reader]['datasets'].items():
            file_type = self.settings.readers[reader]['file_types'][dictionary['file_type']]
            filenames_matched = self._get_filenames_matched(filepaths, file_type)
            if any(filenames_matched):
                reader_instances[dataset] = {}
                reader_instances[dataset]['file_names'] = filenames_matched
                reader_instances[dataset]['reader'] = self.load_reader(file_type)
        return reader_instances

    def get_data_in_template(self, data, template=None, resolution='lores_data_all'):
        """
        Appends dataframes to template dataframe
        :param data: Dictionary with data
        :param template: str
        :param resolution: str
        :return: data in template
        """
        template_handler = self.load_template_handler(template)
        for fid in data:
            template_handler.append_to_template(data[fid][resolution])

        template_handler.convert_formats()
        return template_handler.template

    def get_writer_file_name(self, writer):
        """
        #FIXME move elsewhere?
        #Fixme change 'filename' to 'filename_prefix'? perhaps not prefix in all cases?
        :param writer: str
        :return: str, standard filename prefix
        """
        return self.settings.writers[writer]['writer'].get('filename')

    def load_template_handler(self, template):
        """
        :param template: str
        :return: Template instance
        """
        template_instance = self.settings.templates[template].get('template_handler')
        return template_instance(self.settings)

    def load_reader(self, file_type):
        """
        :param file_type: Dictionary
        :return: Reader instance
        """
        reader_instance = file_type.get('file_reader')
        return reader_instance(self.settings)

    def load_writer(self, writer):
        """
        :param writer: str
        :return: Writer instance
        """
        writer_instance = self.settings.writers[writer]['writer'].get('writer')
        return writer_instance(self.settings)

    def save_data(self, datasets, file_name=None, save_path=None, writer=None, return_data_path=False):
        """
        #TODO Needs to be more flexible. Savepath should be dealt with within each writer?
        :param datasets: list of different types of datasets. Can be metadata and profile data
        :param file_name: str
        :param save_path: str
        :param writer: writer instance
        :param return_data_path: False or True
        :return: Data is saved.
                 If return_data_path: str, data saved with this path
        """
        if save_path is None:
            save_path = self.settings.settings_paths.get('export_path')
        if file_name is None:
            file_name = self.get_writer_file_name(writer)
        if not save_path.endswith('\\') and not save_path.endswith('/'):
            save_path = '/'.join([save_path, file_name])
        else:
            save_path = ''.join([save_path, file_name])

        writer = self.load_writer(writer)
        writer.write(datasets)
        # writer.write(datasets, save_path)
        if return_data_path:
            return writer.data_path

    def create_archive(self, data_path=None):
        """
        :param data_path: str, path to data folder
        :return: Data written to archive structure
        """
        archive = Archive(self.settings)
        archive.write_archive_package(data_path)
        recieved_data = self._get_loaded_filenames()
        archive.import_received_data(recieved_data)

    def _get_loaded_filenames(self):
        """
        :return: List of filenames that have been loaded in Session
        """
        recieved_data = []
        for dset in self.readers:
            recieved_data.extend(self.readers[dset]['file_names'])
        return recieved_data

    def update_settings_attributes(self, **dictionary):
        """
        #FIXME Do we need to add attributes of specified reader to a higer level within the self.settings structure?
        :param dictionary: Dictionary (E.g. reader settings)
        :return: self.settings with specified reader kwargs at a higher level within the settings dictionary tree
        """
        self.settings.set_attributes(self.settings, **dictionary)
