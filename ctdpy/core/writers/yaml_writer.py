# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 09:48:18 2018

@author: a002028
"""
import yaml
import numpy as np
import pandas as pd


class YAMLwriter(dict):
    """
    """
    def __init__(self):
        super().__init__()

    def _check_format(self, out_file):   
        """
        :param out_file: Dictionary, pd.DataFrame
        :return:
        """
        if isinstance(out_file, dict):
            return out_file
        elif isinstance(out_file, pd.DataFrame):
            return out_file.to_dict()
        elif isinstance(out_file, np.ndarray):
            raise NotImplementedError('Array to dictionary?')
            #FIXME possible in-format?
        else:
            return None

    def write_yaml(self, out_file, out_path='', indent=4):
        """
        :param out_file: Preferably dictionary or pd.DataFrame
        :param out_path: str
        :param indent: int
        :return: Saved yaml file
        """
        out_file = self._check_format(out_file)
        with open(out_path, 'w') as path:
            yaml.safe_dump(out_file, path, indent=indent, default_flow_style=False)


if __name__ == '__main__':
    yw = YAMLwriter()
    import json
    j_path = 'C:/Utveckling/algaware/etc/plot_setup.json'
    with open(j_path, 'r') as fd:
        setup = json.load(fd)



    setup['function_types'] = {'date_locator': "!!python/name:plot.functions.MPLDatelocator ''",
                               'date_formatter': "!!python/name:plot.functions.MPLDateformatter ''"}

    setup['algaware']['figures']['The Skagerrak']['axes']['7']['x_axis']['major_locator'] = {'style': 'month',
                                                                                             'args': [],
                                                                                             'kwargs': {},
                                                                                             'function': 'date_locator'}

    setup['algaware']['figures']['The Skagerrak']['axes']['7']['x_axis']['major_formatter'] = {'style': 'date',
                                                                                             'args': [''],
                                                                                             'kwargs': {},
                                                                                             'function': 'date_formatter'}

    setup['algaware']['figures']['The Skagerrak']['axes']['7']['x_axis']['minor_locator'] = {'style': 'month',
                                                                                             'args': [],
                                                                                             'kwargs': {'bymonthday': 15},
                                                                                             'function': 'date_locator'}

    setup['algaware']['figures']['The Skagerrak']['axes']['7']['x_axis']['minor_formatter'] = {'style': 'date',
                                                                                               'args': ['%b'],
                                                                                               'kwargs': {},
                                                                                               'function': 'date_formatter'}

    yw.write_yaml(setup, out_path=j_path.replace('.json', '.yaml'))
