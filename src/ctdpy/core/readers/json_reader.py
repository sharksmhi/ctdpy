# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 08:46:00 2018

@author: a002028
"""
import json
import numpy as np
import pandas as pd
from ctdpy.core import utils


class JSONreader:
    """Reader for json-files.

    - Import json
    - Export to json
    - Find dictionary within json file based on a specific key
    - Add elements to dictionary
    - Fill up json/dictionary structure with relevant/desired information
    """

    def __init__(self):
        """Initialize."""
        super().__init__()
        self.config = {}

    def _export_json(self, data_dict=None, out_source='', indent=4):
        """Export data to file."""
        if data_dict is None:
            data_dict = {}
        if isinstance(data_dict, pd.DataFrame):
            data_dict = self._get_dict(df=data_dict)

        with open(out_source, "w") as outfile:
            json.dump(data_dict, outfile, indent=indent)

    def export(self, out_source='', out_file=None):
        """Export data to file."""
        if out_file:
            self._export_json(out_source=out_source,
                              data_dict=out_file)
        elif hasattr(self, 'out_file'):
            self._export_json(out_source=out_source,
                              data_dict=self.out_file)
        elif hasattr(self, 'config'):
            self._export_json(out_source=out_source,
                              data_dict=self.config)
        else:
            raise UserWarning('No outfile specified for export to .json')

    def find_key(self, key, dictionary):
        """Generate path to an element within the given dictionary.

        Note that a key can occur multiple times in a nested dictionary.
        """
        if isinstance(dictionary, list):
            for d in dictionary:
                for result in self.find_key(key, d):
                    yield result
        else:
            for k, v in dictionary.items():
                if k == key:
                    yield v
                elif isinstance(v, dict):
                    for result in self.find_key(key, v):
                        yield result
                elif isinstance(v, list):
                    for d in v:
                        for result in self.find_key(key, d):
                            yield result

    def load_json(self, config_files=None, return_config=False):
        """Load json files.

        Args:
            config_files: will be either a list of dictionaries or one
                          single dictionary depending on what the
                          json file includes
            return_config: False | True
        """
        config_files = config_files or []
        if not isinstance(config_files, (list, np.ndarray)):
            config_files = [config_files]

        for config_file in config_files:
            with open(config_file, 'r') as fd:
                self.config = utils.recursive_dict_update(
                    self.config, json.load(fd)
                )

        if return_config:
            return self.config

    def setup_dict(self, keys=None):
        """Set dictionary based on list of keys."""
        keys = keys or []
        return {key: True for key in keys}
