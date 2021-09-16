# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 14:41:47 2018

@author: a002028
"""
import numpy as np


class Profile:
    """ Handles one profile at a time
    """
    def __init__(self, data=None):
        self.data = data

    def update_data(self, data=None):
        """
        :param data: pd.DataFrame
        :return: Writes over self.data
        """
        self.data = data

    def extract_lores_data(self, key_depth=None, discrete_depths=None):
        """
        Get data from discrete depths based on discrete_depths
        :param key_depth: str
        :param discrete_depths: list, discrete depths
        :return: pd.DataFrame
        """
        discrete_depths = discrete_depths or []
        idx = self._get_index_array(key_depth, discrete_depths)
        return self.data.iloc[idx, :]

    def _get_index_array(self, key, depths):    
        """
        Extract indices for discrete depth
        :param key: str
        :param depths: list
        :return: index array
        """
        hires_dep = self.data[key].values.astype(float)
        qf_pres = 'Q_PRES_CTD'
        if qf_pres in self.data:
            hires_dep[self.data[qf_pres] == 'B'] = -999
        idx = [(np.abs(hires_dep-dep)).argmin() for dep in depths if dep <= hires_dep.max()]
        idx = self._append_maximum_depth_index(idx, hires_dep)
        return sorted(set(idx))

    @staticmethod
    def _append_maximum_depth_index(idx, array):
        """
        Allways append max depth index
        :param idx: index array
        :param array: array with depth
        :return: extended index array
        """
        maxdep_idx = np.where(array == array.max())[0][0]
        if maxdep_idx not in idx:
            idx.append(maxdep_idx)
        return idx
