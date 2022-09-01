# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 15:54:41 2018

@author: a002028
"""
import os
import glob
from trollsift.parser import globify
from ctdpy.core.readers.txt_reader import load_txt
from ctdpy.core.readers.file_handlers import BaseFileHandler
from ctdpy.core import utils


class CNVreader(BaseFileHandler):
    """Reader for cnv files."""

    def select_files_from_directory(self, directory=None):
        """Return files that matches the given reader.

        Find files for this reader in *directory*.
        If directory is None or '', look in the current directory.
        """
        filenames = []
        directory = directory or ''
        for pattern in self.file_patterns:
            matching = glob.iglob(os.path.join(directory, globify(pattern)))
            filenames.extend(matching)
        return filenames

    def get_file_list_match(self, file_directory):
        """Return list of matching files."""
        file_list = os.listdir(file_directory)
        return utils.get_file_list_match(
            file_list, self.settings.reader['suffix']
        )

    @staticmethod
    def load(fid, sep='\t', as_series=False, **kwargs):
        """Load "fid"."""
        return load_txt(file_path=fid, separator=sep, as_dtype=True, **kwargs)
