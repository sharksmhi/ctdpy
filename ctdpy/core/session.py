# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 10:50:49 2018

@author: a002028

"""
from ctdpy.core import config, data_handlers
from ctdpy.core.profile import Profile
from ctdpy.core.archive_handler import Archive
from ctdpy.core.utils import (
    get_file_list_based_on_suffix,
    match_filenames,
)


class Session:
    """The Main Class for ctdpy.

    Example usage:

        from ctdpy.core.session import Session
        from ctdpy.core.utils import generate_filepaths

        # Create generator for cnv-files.
        files = generate_filepaths('/path/to/files/', endswith='.cnv')

        # Create reader.
        s = Session(filepaths=files, reader='smhi')

        # Load data.
        datasets = s.read()

        # Save data with a given writer.
        # Datasets are stored in a list of 2 (0: data, 1: metadata). For this example we only have data, no metadata.
        s.save_data(datasets[0], writer='metadata_template')
    """

    def __init__(self, filepaths=None, reader=None, export_path=None):
        """Initialize settings object, create reader instance and set path to export path.

        Args:
            filepaths (iterable): A sequence of files that will be used to load data from.
            reader (str): Name of reader.
            export_path (str): Path to export path.
        """
        self.settings = config.Settings()
        if export_path:
            self.settings.update_export_path(export_path)

        self.readers = None
        if filepaths and reader:
            self.update_settings_attributes(**self.settings.readers[reader])

            filepaths = list(filepaths)
            self.readers = self.create_reader_instances(filepaths=filepaths, reader=reader)

    def read(self, add_merged_data=False, add_low_resolution_data=False):
        """Load data and return dataset.

        Args:
            add_merged_data (bool): WILL PROBABLY BE MOVED AND USED ELSEWHERE.
                                    False or True. Merge metadata and data into template.
            add_low_resolution_data (bool): WILL PROBABLY BE MOVED AND USED ELSEWHERE.
                                            Include extra pd.DataFrame for low resolution data
        """
        if add_merged_data:
            raise FutureWarning('The functionality of ctdpy.core.session.Session.read(add_merged_data=True)'
                                'will be moved elsewhere in the future.')
        if add_low_resolution_data:
            raise FutureWarning('The functionality of ctdpy.core.session.Session.read(add_low_resolution_data=True)'
                                'will be moved elsewhere in the future.')
        datasets = self._read_datasets(add_merged_data, add_low_resolution_data)
        return datasets

    def _read_datasets(self, add_merged_data, add_low_resolution_data):
        """Read and return datasets.

        Different "datasets" for one type of data (e.g. seabird_smhi).
        Could be both cnv and xlsx files (metadata and data seperated in different files but belong together).

        Args:
            add_merged_data (bool): WILL PROBABLY BE MOVED AND USED ELSEWHERE.
                                    False or True. Merge metadata and data into template.
            add_low_resolution_data (bool): WILL PROBABLY BE MOVED AND USED ELSEWHERE.
                                            Include extra pd.DataFrame for low resolution data
        """
        # TODO Merge the different datasets?
        datasets = []
        for dataset in self.readers:
            data = self.readers[dataset]['reader'].get_data(
                filenames=self.readers[dataset]['file_names'],
                add_low_resolution_data=add_low_resolution_data
            )

            # TODO add_merged_data will ONLY merge profile data with meta data into PHYCHE-template.
            #  We should therefore do this elsewhere
            if add_merged_data and add_low_resolution_data:
                self.readers[dataset]['reader'].merge_data(data, resolution='lores_data')

            datasets.append(data)

        return datasets

    @staticmethod
    def _get_filenames_matched(filenames, file_type):
        """Get matching filenames."""
        if file_type.get('file_patterns'):
            filenames_matched = match_filenames(filenames, file_type['file_patterns'])
        elif 'file_suffix' in file_type:
            filenames_matched = get_file_list_based_on_suffix(filenames, file_type['file_suffix'])
        else:
            raise ImportWarning('No file_pattern nor suffix is readable in reader.file_types')
        return filenames_matched

    def create_reader_instances(self, filepaths=None, reader=None):
        """Find readers and return their instances."""
        # TODO Redo and move to utils.py or __init__.py
        reader_instances = {}
        for dataset, dictionary in self.settings.readers[reader]['datasets'].items():
            file_type = self.settings.readers[reader]['file_types'][dictionary['file_type']]
            filenames_matched = self._get_filenames_matched(filepaths, file_type)
            if any(filenames_matched):
                reader_instances[dataset] = {}
                reader_instances[dataset]['file_names'] = filenames_matched
                reader_instances[dataset]['reader'] = self.load_reader(file_type)
        return reader_instances

    def get_data_in_template(self, datasets, template=None, resolution='lores'):
        """Append dataframes to template dataframe.

        Args:
            datasets (dict): data
            template (str): Name of template to use.
            resolution (str): 'hires' / 'lores'
        """
        template_handler = self.load_template_handler(template)
        profile = None
        if resolution == 'lores':
            profile = Profile()

        meta_handler = data_handlers.MetaHandler(self.settings)
        for fid in datasets:
            if resolution == 'lores':
                profile.update_data(data=datasets[fid]['data'])
                data = profile.extract_lores_data(key_depth='DEPH [m]', discrete_depths=self.settings.depths)
            else:
                data = datasets[fid]['data']

            meta = meta_handler.get_meta_dict(
                datasets[fid]['metadata'],
                keys=self.settings.templates[template]['template'].get('meta_parameters'),
                identifier='//METADATA',
                separator=';',
            )

            template_handler.append_to_template(data, meta=meta)

        return template_handler.template

    def get_writer_file_name(self, writer):
        """Get filename specification for the given writer."""
        # Fixme change 'filename' to 'filename_prefix'? perhaps not prefix in all cases?
        return self.settings.writers[writer]['writer'].get('filename')

    def load_template_handler(self, template):
        """Return Template instance."""
        template_instance = self.settings.templates[template].get('template_handler')
        return template_instance(self.settings)

    def load_reader(self, file_type):
        """Return Reader instance."""
        reader_instance = file_type.get('file_reader')
        return reader_instance(self.settings)

    def load_writer(self, writer):
        """Return Writer instance."""
        writer_instance = self.settings.writers[writer]['writer'].get('writer')
        return writer_instance(self.settings)

    def save_data(self, datasets, save_path=None, writer=None,
                  return_data_path=False, **writer_kwargs):
        """Save datasets.

        Args:
            datasets (list): list of datasets. Eg. metadata and profile data.
            save_path (str): path to export folder.
            writer (object): writer instance
            return_data_path (bool): False or True
        """
        if save_path:
            self.settings.update_export_path(save_path)

        writer = self.load_writer(writer)
        writer.write(datasets, **writer_kwargs)
        if return_data_path:
            return writer.data_path

    @staticmethod
    def update_metadata(datasets=None, metadata=None, overwrite=False):
        """Update the given datasets with information in metadata. Option to overwrite."""
        datasets = datasets or []
        metadata = metadata or {}
        for dataset in datasets.values():
            for key, value in metadata.items():
                current_value = dataset['metadata'].get(key, None)
                if current_value and not overwrite:
                    continue
                dataset['metadata'][key] = value

    def create_archive(self, data_path=None):
        """Create standard archive folder structure, and place data therein."""
        archive = Archive(self.settings)
        archive.write_archive_package(data_path)
        recieved_data = self._get_loaded_filenames()
        archive.import_received_data(recieved_data)

    def _get_loaded_filenames(self):
        """Return list of filenames that have been loaded in Session."""
        recieved_data = []
        for dset in self.readers:
            recieved_data.extend(self.readers[dset]['file_names'])
        return recieved_data

    def update_settings_attributes(self, **dictionary):
        """Update setting attributes.

        Settings with specified reader kwargs at a higher level within the settings dictionary tree.

        Args:
            dictionary: kwargs, eg. reader settings
        """
        # FIXME Do we need to add attributes of specified reader to a higer level within the self.settings structure?
        self.settings.set_attributes(self.settings, **dictionary)
