# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 15:54:41 2018

@author: a002028
"""
import os
import glob
from trollsift.parser import globify, parse
from ctdpy.core.readers.txt_reader import load_txt
from ctdpy.core.readers.file_handlers import BaseFileHandler
from ctdpy.core import utils


class CNVreader(BaseFileHandler):
    """
    """
    # def __init__(self, settings):
    #     super().__init__()
    #     self.settings = settings
    #     self.reader_path_name = utils.get_object_path(CNVreader)

    def select_files_from_directory(self, directory=None):
        """
        Find files for this reader in *directory*.
        If directory is None or '', look in the current directory.
        :param directory: str, path to directory
        :return: list of matching paths
        """
        filenames = []
        if directory is None:
            directory = ''
        for pattern in self.file_patterns:
            matching = glob.iglob(os.path.join(directory, globify(pattern)))
            filenames.extend(matching)
        return filenames

    def get_file_list_match(self, file_directory):
        """

        :param file_directory: str, path to directory
        :return: list of matching paths
        """
        file_list = os.listdir(file_directory)
        
        return utils.get_file_list_match(file_list, self.settings.reader['suffix'])

    @staticmethod
    def load(fid, sep='\t', as_series=False):
        """
        :param fid: str, file path
        :param sep: str, seperator
        :param as_series: NotImplementedError
        :return: pd.DataFrame (or pd.Series?)
        """
        return load_txt(file_path=fid, seperator=sep, as_dtype=True)
