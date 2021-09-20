# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 13:38:35 2018

@author: a002028
"""
import os
import zipfile


class ZipWriter:
    """Writer of zip files."""

    def __init__(self):
        """Initialize."""
        pass

    def write(self, folder_with_archives, save_path_for_zipfiles):
        """Write to zip."""
        def append_sub_directory(folder_name):
            root_len = len(dataset_name)
            for root, _, files in os.walk(dataset_name + folder_name):
                for filename in files:
                    filenamepath = ''.join([root, '/', filename])
                    ziparchive.appendFile(filenamepath, filenamepath[root_len:])

        archive_list = os.listdir(folder_with_archives)

        # Iterate over datasets.
        for dataset_name in archive_list:
            ziparchive = ZipArchive(dataset_name, save_path_for_zipfiles)

            # Copy metadata from dataset root level.
            shark_meta_name = dataset_name + '/shark_metadata.txt'
            if os.path.exists(shark_meta_name):
                ziparchive.appendFile(shark_meta_name, 'shark_metadata.txt')

            # Copy processed content.
            if os.path.exists(dataset_name + '/processed_data'):
                append_sub_directory('/processed_data')
            if os.path.exists(dataset_name + '/received_data'):
                append_sub_directory('/received_data')


class ZipArchive:
    """ZipArchive handler."""

    def __init__(self, zip_file_name, zip_dir_path=None):
        """Initialize and check format of zip-path."""
        if zip_dir_path:
            self._filepathname = os.path.join(zip_dir_path, zip_file_name)
        else:
            self._filepathname = zip_file_name
        # Delete old version, if exists.
        if os.path.exists(self._filepathname):
            os.remove(self._filepathname)

    def appendFile(self, file_name_path, file_name_in_zip):
        """Append file to zip."""
        ziparchive = None
        try:
            ziparchive = zipfile.ZipFile(self._filepathname, 'a', zipfile.ZIP_DEFLATED)
            ziparchive.write(file_name_path, arcname=file_name_in_zip)
        finally:
            if ziparchive:
                ziparchive.close()

    def appendZipEntry(self, zip_entry_name, content):
        """Add entry."""
        ziparchive = None
        try:
            ziparchive = zipfile.ZipFile(self._filepathname, 'a')
            ziparchive.writestr(zip_entry_name, content)
        finally:
            if ziparchive:
                ziparchive.close()
