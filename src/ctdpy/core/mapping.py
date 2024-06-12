# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 13:47:52 2018

@author: a002028
"""
import pandas as pd
import logging

logger = logging.getLogger(__file__)


class AttributeDict(dict):
    """Base class for attribute dictionaries."""

    def __init__(self):
        """Initialize."""
        super().__init__()

    def _add_arrays_to_entries(self, **entries):
        """Add arrays as attributes to self."""
        for key, array in entries.items():
            # TODO Check if array is needed if only one value
            setattr(self, key, array)

    def add_entries(self, **entries):
        """Turn elements in arrays into attributes.

        For mapping purposes with a corresponding official field name.

        Example key and list:
        "SALT2_CTD": [
            "SALT2_CTD [psu (PSS-78)]",
            "Salthalt2",
            "sal11: Salinity, Practical, 2 [PSU]"
        ]

        Here all values in the list will be mapped to "SALT2_CTD".
        """
        for key, array in entries.items():
            setattr(self, key, key)
            setattr(self, key.lower(), key)

            if isinstance(array, pd.core.series.Series):
                array = array.values

            for value in array:
                if not pd.isnull(value):
                    setattr(self, value, key)
                    setattr(self, value.lower(), key)

    def add_entries_from_keylist(self, data, from_combo_keys=None,
                                 from_synonyms=None, to_key=''):
        """Create mapping attributes for ShipMapping().

        Args:
            data (dict):
            from_combo_keys (list): list of keys
            from_synonyms (list): list of keys
            to_key (str):
        """
        from_combo_keys = from_combo_keys or []
        from_synonyms = from_synonyms or []

        for i, value in enumerate(data[to_key]):
            setattr(self, value, value)
            if any(from_combo_keys):
                setattr(self, ''.join([
                    data[key][i].zfill(2) for key in from_combo_keys
                ]), value)
            if any(from_synonyms):
                for key in from_synonyms:
                    setattr(self, data[key][i], value)
                    setattr(self, data[key][i].upper(), value)

    def keys(self):
        """Return list of keys from self attributes."""
        return list(self.__dict__.keys())

    def get(self, key):
        """Get attribute from self using key."""
        logger.info(f'{key=}')
        try:
            logger.debug(
                f'try getting attribute: {key} -> {getattr(self, key)}')
            # if key == '77SN':
            #     raise
            return getattr(self, key)
        except AttributeError:
            try:
                logger.debug(
                    f'try getting attribute (lower): '
                    f'{key.lower()} -> {getattr(self, key)}')
                return getattr(self, key.lower())
            except Exception:
                if '[' in key:
                    try:
                        key = key.split('[')[0].strip()
                        return getattr(self, key.lower())
                    except Exception:
                        logger.warning(f'No mapping found for key ([): {key}')
                        return key
                else:
                    logger.warning(f'No mapping found for key: {key}')
                    return key

    def get_list(self, key_list):
        """Get list of values from self attributes based on key_list."""
        return [self.get(key) for key in key_list]

    def get_mapping_dict(self, key_list):
        """Get dictionary from self attributes based on key_list."""
        return dict([(key, self.get(key)) for key in key_list])

    def __getitem__(self, key):
        """Get item from self. If not key exists return None"""
        return getattr(self, key)


class ParameterMapping(AttributeDict):
    """Imports parameter mapping file."""

    def __init__(self):
        """Initialize."""
        super().__init__()

    def map_parameter_list(self, para_list, ext_list=False):
        """Return mapped parameter list.

        Args:
            para_list (list): list of parameters
            ext_list (bool): False or True, NotImplemented
        """
        return self.get_list(para_list)

    def get_parameter_mapping(self, para_list, ext_list=False):
        """Get a dictionary with mapped parameters from the given para_list."""
        return self.get_mapping_dict(para_list)


class ShipMapping(AttributeDict):
    """Load file to map 2sign-cntry and 2sign-shipc to 4sign-shipc."""

    def __init__(self):
        """Initialize."""
        super().__init__()

    def map_cntry_and_shipc(self, cntry=None, shipc=None):
        """Get SHIP code (according to standard of ICES)."""
        return self.get(cntry + shipc)

    def map_shipc(self, cntry_shipc):
        """Map SHIP code (according to standard of ICES)."""
        return self.get(cntry_shipc)
