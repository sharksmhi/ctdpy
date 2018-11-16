# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 14:23:22 2018

@author: a002028
"""

import os
from collections import Mapping
import core
#from six.moves import configparser

#==============================================================================


def recursive_dict_update(d, u):
    """ Recursive dictionary update using
    Copied from:
        http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
        via satpy
    """
    for k, v in u.items():
        if isinstance(v, Mapping):
            r = recursive_dict_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d

"""
#==============================================================================
#==============================================================================
"""


class Settings(object):
    """
    """
    def __init__(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        etc_path = '/'.join([self.dir_path, 'core', 'etc', ''])
        self._load_settings(etc_path)
        self._check_local_paths()
        self._setup_parameter_mapping()

    def __setattr__(self, name, value):
        """
        Defines the setattr for object self
        :param name: str
        :param value: any kind
        :return:
        """
        if name == 'dir_path':
            pass
        elif isinstance(value, str) and 'path' in name:
            name = ''.join([self.dir_path, value])
        elif isinstance(value, dict) and 'paths' in name:
            self._check_for_paths(value)
        super().__setattr__(name, value)

    def _check_local_paths(self):
        """
        Checks paths in settings_paths..
        :return:
        """
        #FIXME Näh, så här kan vi inte ha det..
        for path in self.settings_paths:
            if not os.path.exists(self.settings_paths.get(path)) and '.' not in self.settings_paths.get(path):
                os.makedirs(self.settings_paths.get(path))

    def _check_for_paths(self, dictionary):
        """
        Since default path settings are set to ctdpy base folder
        we need to add that base folder to all paths
        :param dictionary: Dictionary with paths as values and keys as items..
        :return: Updates dictionary with local path (self.dir_path)
        """
        for item, value in dictionary.items():
            if isinstance(value, dict):
                self._check_for_paths(value)
            elif 'path' in item:
                dictionary[item] = ''.join([self.dir_path, value])

    def _load_settings(self, etc_path):
        """
        :param etc_path: str, local path to settings
        :return: Updates attributes of self
        """
        paths = self.get_filepaths_from_directory(etc_path)
        settings = core.readers.YAMLreader().load_yaml(paths, return_config=True)
        self.set_attributes(self, **settings)
        subdirectories = self.get_subdirectories(etc_path)

        for subdir in subdirectories:
            subdir_path = '/'.join([etc_path, subdir, ''])
            paths = self.get_filepaths_from_directory(subdir_path)
            sub_settings = core.readers.YAMLreader().load_yaml(paths,
                                                               file_names_as_key=True,
                                                               return_config=True)
            self._check_for_paths(sub_settings)
            self._set_sub_object(subdir, sub_settings)

    def set_reader(self, reader):
        """
        :param reader: str
        :return: Includes reader kwargs as attributes to self
        """
        self.set_attributes(self, **self.readers[reader])

    def set_writer(self, writer=None):
        """
        :param writer: str
        :return: Includes writer kwargs as attributes to self
        """
        self.set_attributes(self, **self.writers.get(writer))

    def _set_sub_object(self, attr, value):
        """
        :param attr: str, attribute
        :param value: any kind
        :return: Updates attributes of self
        """
        setattr(self, attr, value)

    # @classmethod
    def _setup_parameter_mapping(self):
        """
        #FIXME god damn it! where does self.parameter_mapping come from???..
        Creates parameter mapping object within self
        :return:
        """
        self.pmap = core.mapping.ParameterMapping()
        self.pmap.add_entries(**self.parameter_mapping)

    @staticmethod
    def set_attributes(obj, **kwargs):
        """
        #TODO Move to utils?
        With the possibility to add attributes to an object which is not 'self'
        :param obj: object
        :param kwargs: Dictionary
        :return: sets attributes to object
        """
        for key, value in kwargs.items():
            setattr(obj, key, value)

    @staticmethod
    def generate_filepaths(directory, pattern=''):
        """
        #TODO Move to utils?
        :param directory: str, directory path
        :param pattern: str
        :return: generator
        """
        for path, subdir, fids in os.walk(directory):
            for f in fids:
                if pattern in f:
                    yield os.path.abspath(os.path.join(path, f))

    @staticmethod
    def get_subdirectories(directory):
        """
        :param directory: str, directory path
        :return: list of existing directories (not files)
        """
        return [subdir for subdir in os.listdir(directory)
                if os.path.isdir(os.path.join(directory, subdir))]

    @staticmethod
    def get_filepaths_from_directory(directory):
        """
        :param directory: str, directory path
        :return: list of files in directory (not sub directories)
        """
        return [''.join([directory, fid]) for fid in os.listdir(directory)
                if not os.path.isdir(directory+fid)]
