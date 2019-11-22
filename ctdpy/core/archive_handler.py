# -*- coding: utf-8 -*-
"""
Created on Wen Oct 31 10:26:30 2018

@author: a002028
"""

import os
import utils

class Archive(object):
    """
    
    """
    def __init__(self, settings, data_path=''):
        self.settings = settings
        self.data_path = data_path
        # self.archive_structure = self._get_standard_archive_structure()

    def write_archive_package(self, data_path):
        """
        :param path: folder with data files
        :return:
        """
        self._copy_standard_archive_structure()
        self._copy_data_files_to_archive_path(data_path)

    def _copy_data_files_to_archive_path(self, data_path):
        """
        :param data_path: Path to data files
        :return: Copies datafiles to archive_data_path
        """
        archive_data_path = self._get_data_path_in_archive()
        utils.copytree(data_path, archive_data_path)

    def _get_data_path_in_archive(self):
        """
        :return:
        """
        return '/'.join([self.archive_path, 'processed_data', ''])

    def _get_received_data_path_in_archive(self):
        """
        :return:
        """
        return '/'.join([self.archive_path, 'received_data', ''])

    def _copy_standard_archive_structure(self):
        """
        :return:
        """
        source_path = self._get_standard_archive_structure()
        self.archive_path = self._get_destination_path()
        utils.copytree(source_path, self.archive_path)

    def load_standard_archive_files(self):
        """
        :return:
        """
        raise NotImplementedError
        # generator = utils.generate_strings_based_on_suffix(self.archive_structure, '.txt')
        # files = [filename for filename in generator]

    def _get_destination_path(self, archive_name='archive_'):
        """
        :return: Path to new archive
        """
        folder_time_stamp = utils.get_datetime_now(fmt='%Y%m%d_%H%M%S')
        return ''.join([self.settings.settings_paths.get('export_path'),
                        archive_name, folder_time_stamp])

    def _get_standard_archive_structure(self):
        """
        :return: archive_structure_path
        """
        return self.settings.settings_paths.get('archive_structure_path')

    def import_received_data(self, file_paths):
        """
        :param file_paths:
        :return:
        """
        target_path = self._get_received_data_path_in_archive()
        for fid in file_paths:
            utils.copyfile(fid, target_path)

    def _load_zipwriter_instance(self):
        """
        :return: Writer
        """
        writer_instance = self.settings.writers['zip']['writer'].get('writer')
        return writer_instance()

    def zip_archive(self):
        """
        :return: Zipped archive ready for sharkweb to load
        """
        zipzy = self._load_zipwriter_instance()

