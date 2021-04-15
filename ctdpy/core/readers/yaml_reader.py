# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 10:29:30 2018

@author: a002028
"""
import os

from ctdpy.core import utils
import numpy as np
import yaml


def get_filebase(path, pattern):
    """Get the end of *path* of same length as *pattern*."""
    # A pattern can include directories
    tail_len = len(pattern.split(os.path.sep))
    return os.path.join(*path.split(os.path.sep)[-tail_len:])


class YAMLreader(dict):
    """
    """
    def __init__(self):
        super().__init__()

        self.config = {}

    def load_yaml(self, config_files, file_names_as_key=False, return_config=False):
        """

        :param config_files: Preferably list of file paths
        :param file_names_as_key: False | True
        :param return_config: False | True
        :return: Dictionary with loaded files specifications
        """
        if not isinstance(config_files, (list, np.ndarray)):
            config_files = [config_files]

        for config_file in config_files:
            with open(config_file) as fd:
                try:
                    file = yaml.load(fd, Loader=yaml.FullLoader)
                except yaml.YAMLError:
                    file = yaml.safe_load(fd)
                # file = yaml.load(fd)
                # print('config_file', config_file)
                # print(file)
                if file_names_as_key:
                    file_name = self.get_file_name(config_file)
                    self.config[file_name] = file
                else:
                    self.config = utils.recursive_dict_update(self.config, file)

        if return_config:
            return self.config

    @staticmethod
    def get_file_name(file_path):
        """
        :param file_path: str, complete path to file
        :return: filename without extension
        """
        filename = os.path.basename(file_path)
        return os.path.splitext(filename)[0]
