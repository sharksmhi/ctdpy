# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 09:48:18 2018

@author: a002028
"""
import yaml
import numpy as np
import pandas as pd


class YAMLwriter(dict):
    """Writer of yaml files."""

    # TODO Ever used?

    def __init__(self):
        """Initialize."""
        super().__init__()

    def _check_format(self, data):
        """Check format of data."""
        if isinstance(data, dict):
            return data
        elif isinstance(data, pd.DataFrame):
            return data.to_dict()
        elif isinstance(data, np.ndarray):
            raise NotImplementedError('Array to dictionary?')
            # FIXME possible in-format?
        else:
            return None

    def write_yaml(self, data, out_path='', indent=4):
        """Write to yaml-file.

        Args:
            data: Preferably dictionary or pd.DataFrame
            out_path: Full path to file
            indent (int): Indent length
        """
        data = self._check_format(data)
        with open(out_path, 'w') as path:
            yaml.safe_dump(
                data,
                path,
                indent=indent,
                default_flow_style=False
            )
