# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 14:23:22 2018

@author: a002028
"""
import os
from typing import Mapping
from ctdpy.core import readers, mapping


class Settings:
    """Settings class for ctdpy."""

    def __init__(self):
        """Load all static files."""
        # TODO Handling of paths should be dealt with using pathlib instead.
        self.dir_path = os.path.dirname(
            os.path.realpath(__file__)).replace('\\core', '')
        etc_path = '\\'.join([self.dir_path, 'core', 'etc', ''])
        self.user = os.path.expanduser('~').split('\\')[-1]
        self._load_settings(etc_path)
        self._check_local_paths()
        self._setup_mapping_parameter()
        self._setup_mapping_ship()
        self._check_archive_folder_structure()

    def __setattr__(self, name, value):
        """Define the setattr for self."""
        if name == 'dir_path':
            pass
        elif isinstance(value, str) and 'path' in name:
            name = ''.join([self.dir_path, value])
        elif isinstance(value, dict) and 'paths' in name:
            self._check_for_paths(value)
        super().__setattr__(name, value)

    def update_export_path(self, new_path):
        """Update path to export directory."""
        if new_path:
            if os.path.isdir(new_path):
                self.settings_paths['export_path'] = new_path
                print('new export path: %s'
                      % self.settings_paths['export_path'])
            else:
                try:
                    os.makedirs(new_path)
                    self.settings_paths['export_path'] = new_path
                    print('new export path: %s'
                          % self.settings_paths['export_path'])
                except BaseException:
                    raise Warning('Could not change export path, the given path'
                                  ' is not valid: %s \n using default'
                                  ' export path' % new_path)

    def _check_archive_folder_structure(self):
        """Create the "received_data" folder.

        It is an empty folder, and hence might need to be created.
        """
        received_folder = os.path.join(
            self.settings_paths['archive_structure_path'], 'received_data'
        )
        if not os.path.exists(received_folder):
            os.makedirs(received_folder)

    def _check_local_paths(self):
        """Check paths in settings_paths."""
        # FIXME Näh, så här kan vi inte ha det..

        for path in self.settings_paths:
            if not os.path.exists(self.settings_paths.get(path)) and \
                    '.' not in self.settings_paths.get(path):
                os.makedirs(self.settings_paths.get(path))

    def _check_for_paths(self, dictionary):
        """Save pathways from dictionary.

        Since default path settings are set to ctdpy base folder
        we need to add that base folder to all paths.

        Args:
             dictionary: Dictionary with paths as values and keys as items.
        """
        for item, value in dictionary.items():
            if isinstance(value, dict):
                self._check_for_paths(value)
            elif 'path' in item:
                dictionary[item] = ''.join([self.dir_path, value])

    def _load_settings(self, etc_path):
        """Load all settings.

        Args:
            etc_path: local path to settings
        """
        paths = self.get_filepaths_from_directory(etc_path)
        settings = readers.YAMLreader().load_yaml(paths, return_config=True)
        self.set_attributes(self, **settings)
        subdirectories = self.get_subdirectories(etc_path)

        for subdir in subdirectories:
            subdir_path = '/'.join([etc_path, subdir, ''])
            paths = self.get_filepaths_from_directory(subdir_path)
            sub_settings = readers.YAMLreader().load_yaml(
                paths, file_names_as_key=True, return_config=True
            )
            self._check_for_paths(sub_settings)
            self._set_sub_object(subdir, sub_settings)

    def set_reader(self, reader):
        """Set attributes for the given reader."""
        self.set_attributes(self, **self.readers[reader])

    def set_writer(self, writer=None):
        """Set attributes for the given writer."""
        self.set_attributes(self, **self.writers.get(writer))

    def _set_sub_object(self, attr, value):
        """Set attributes."""
        setattr(self, attr, value)

    def _setup_mapping_parameter(self):
        """Create parameter mapping object."""
        # FIXME god damn it!:) where does self.mapping_parameter
        #  come from???.. in .set_attributes()
        self.pmap = mapping.ParameterMapping()
        self.pmap.add_entries(**self.mapping_parameter)

    def _setup_mapping_ship(self):
        """Create ship mapping object within self.

        cntry_head = 'land'
        ship_head = 'SMHI-kod'
        name_head = 'namn'
        to_key = 'kodlista'
        """
        self.smap = mapping.ShipMapping()
        self.smap.add_entries_from_keylist(
            self.mapping_ship,
            from_combo_keys=['land', 'SMHI-kod'],
            from_synonyms=['namn'],
            to_key='kodlista'
        )

    @staticmethod
    def set_attributes(obj, **kwargs):
        """Set attributes.

        With the possibility to add attributes to an
        object which is not 'self'.
        """
        # TODO Move to utils?

        for key, value in kwargs.items():
            setattr(obj, key, value)

    @staticmethod
    def generate_filepaths(directory, pattern=''):
        """Return a generator for file paths."""
        # TODO Move to utils?

        for path, _, fids in os.walk(directory):
            for f in fids:
                if pattern in f:
                    yield os.path.abspath(os.path.join(path, f))

    @staticmethod
    def get_subdirectories(directory):
        """Return list of existing directories (not files)."""
        return [subdir for subdir in os.listdir(directory)
                if os.path.isdir(os.path.join(directory, subdir))]

    @staticmethod
    def get_filepaths_from_directory(directory):
        """Return list of files in directory (not sub directories)."""
        return [''.join([directory, fid]) for fid in os.listdir(directory)
                if not os.path.isdir(directory + fid)]
