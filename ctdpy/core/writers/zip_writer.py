# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 13:38:35 2018

@author: a002028
"""
import os
import zipfile


class ZipWriter:
    """ """
    #TODO skriv klart!
    def __init__(self):
        pass
    # def __init__(self, df, save_path, sheet_name='Data', with_style=False):
    #     pass

    def write(self, folder_with_archives, save_path_for_zipfiles):
        """
        :param folder_to_zip:
        :param save_path:
        :return:
        """
        def append_sub_directory(folder_name):
            root_len = len(dataset_name)
            for root, dirs, files in os.walk(dataset_name + folder_name):
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


    # def _get_dataset_name_and_path(self, dataset_zipfilename_map, dataset_path_map):
    #     """
    #     :param dataset_zipfilename_map:
    #     :param dataset_path_map:
    #     :return:
    #     """
    #     repos_path = item[0].data[u'repos_path']
    #     dataset_name = repos_path.split(u'/')[-1]
    #     date_string = datetime.datetime.fromtimestamp(item[0].data[u'time']).isoformat()
    #     date_string = date_string[0:10]
    #     #
    #     if dataset_name.startswith(u'SHARK_'):
    #         #
    #         zip_file_name = dataset_name + u'_version_' + date_string + u'.zip'
    #         dataset_zipfilename_map[dataset_name] = zip_file_name
    #         #                 dataset_path_map[dataset_name] = work_shark_archive + repos_path.replace(u'/trunk/TEST_SHARK_Archive', u'')
    #         dataset_path_map[dataset_name] = self.work_shark_archive + repos_path.replace(
    #             u'trunk/datasets/' + self.datatype, u'')  ######
    #
    #     return dataset_zipfilename_map, dataset_path_map


class ZipArchive:
    """
    """
    def __init__(self, zip_file_name, zip_dir_path=None):
        """ """
        if zip_dir_path:
            self._filepathname = os.path.join(zip_dir_path, zip_file_name)
        else:
            self._filepathname = zip_file_name
        # Delete old version, if exists.
        if os.path.exists(self._filepathname):
            os.remove(self._filepathname)

    def appendFile(self, file_name_path, file_name_in_zip):
        """
        :param file_name_path:
        :param file_name_in_zip:
        :return:
        """
        ziparchive = None
        try:
            ziparchive = zipfile.ZipFile(self._filepathname, 'a', zipfile.ZIP_DEFLATED)
            ziparchive.write(file_name_path, arcname=file_name_in_zip)
        finally:
            if ziparchive:
                ziparchive.close()

    def appendZipEntry(self, zip_entry_name, content):
        """
        :param zip_entry_name:
        :param content:
        :return:
        """
        ziparchive = None
        try:
            ziparchive = zipfile.ZipFile(self._filepathname, 'a')
            ziparchive.writestr(zip_entry_name, content)
        finally:
            if ziparchive:
                ziparchive.close()
