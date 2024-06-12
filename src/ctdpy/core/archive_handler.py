# -*- coding: utf-8 -*-
"""
Created on Wen Oct 31 10:26:30 2018

@author: a002028
"""
import os
from ctdpy.core import utils


class Archive:
    """Handler for standard SHARK archive."""

    # TODO Fix archive name. Either copy archive structure from Phyche
    #  (eg. SHARK_Profile_BAS_UMSC_2018, SHARK_Profile_GAV_UMSC_2018....)
    #  or simply merge all PROJs as a complete delivery package ?
    #  SHARK_Profile_BAS_GAV_RNE_PBX_XXX_UMSC_2018
    #  or just SHARK_Profile_UMSC_2018

    def __init__(self, settings, data_path=''):
        """Store the settings object."""
        self.settings = settings
        self.data_path = data_path

    def write_archive_package(self, data_path):
        """Copy archive_package and write data to that archive."""
        self._copy_standard_archive_structure()
        self._copy_data_files_to_archive_path(data_path)

    def _copy_data_files_to_archive_path(self, data_path):
        """Copy data files to archive_data_path."""
        archive_data_path = self._get_data_path_in_archive()
        utils.copytree(data_path, archive_data_path)

    def _get_data_path_in_archive(self):
        """Return joined path of archive and processed_data-folder."""
        return '/'.join([self.archive_path, 'processed_data', ''])

    def _get_received_data_path_in_archive(self):
        """Return joined path of archive and received_data-folder."""
        return '/'.join([self.archive_path, 'received_data', ''])

    def _copy_standard_archive_structure(self):
        """Copy standard archive structure (standard according to SHARK)."""
        source_path = self._get_standard_archive_structure()
        self.archive_path = self._get_destination_path()
        utils.copytree(source_path, self.archive_path)

    def load_standard_archive_files(self):
        """NotImplemented."""
        raise NotImplementedError

    def _get_destination_path(self, archive_name='archive_'):
        """Path to new archive."""
        folder_time_stamp = utils.get_datetime_now(fmt='%Y%m%d_%H%M%S')
        return os.path.join(
            self.settings.settings_paths.get('export_path'),
            archive_name + folder_time_stamp
        )

    def _get_standard_archive_structure(self):
        """Get archive structure path."""
        return self.settings.settings_paths.get('archive_structure_path')

    def import_received_data(self, file_paths):
        """Copy original data files to received_data - folder."""
        target_path = self._get_received_data_path_in_archive()
        utils.copytree(None, target_path, file_paths=file_paths)

    def _load_zipwriter_instance(self):
        """Get zip writer."""
        writer_instance = self.settings.writers['zip']['writer'].get('writer')
        return writer_instance()
