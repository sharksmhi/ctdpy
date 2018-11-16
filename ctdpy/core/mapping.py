# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 13:47:52 2018

@author: a002028
"""

import pandas as pd
import numpy as np
from . import readers
#from readers import YAMLreader
"""
#==============================================================================
#==============================================================================
"""


class AttributeDict(dict):
    """ Base class for attribute dictionaries
    """
    def __init__(self):
        super().__init__()

    def _add_arrays_to_entries(self, **entries): 
        """
        Add arrays as attributes to self
        :param entries: Dictionary
        :return:
        """
        for key, array in entries.items(): 
#            if len(array)==1:
#                array = array[0] #FIXME Check if array is needed if only one value
            setattr(self, key, array)

    def add_entries(self, **entries):
        """
        Turns elements in arrays into attributes with a corresponding official field name
        :param entries: Dictionary
        :return:
        """
        for key, array in entries.items():
            setattr(self, key, key)
            setattr(self, key.lower(), key)
            
            if isinstance(array, pd.core.series.Series):
                array = array.values
                
            for value in array:
                if not pd.isnull(value):
                    setattr(self, value.lower(), key)

    def keys(self):
        """
        :return: list of keys from self attributes
        """
        return list(self.__dict__.keys())

    def get(self, key):
        """
        Get attribute from self using key
        :param key: str
        :return: value
        """
        try:
            return getattr(self, key)
        except AttributeError:
            try:
                return getattr(self, key.lower())
            except:
                return key
                print('No mapping found for key: ' + key)
#        finally:
#            print('No mapping found for key: ' + key)

    def get_list(self, key_list):
        """
        :param key_list: list of keys
        :return: list of values from self attributes based on key_list
        """
        return [self.get(key) for key in key_list]

    def get_mapping_dict(self, key_list):
        """
        :param key_list: list of keys
        :return: Dictionary
        """
        return dict([(key, self.get(key)) for key in key_list])

    def __getitem__(self, key):
        """
        :param key: str
        :return: value of self.key
        """
        return getattr(self, key)

"""
#==============================================================================
#==============================================================================
"""


class ParameterMapping(AttributeDict):
    """ Load file to map data fields and parameters to a standard setting format
    """
    def __init__(self):
        super().__init__()

    def load_mapping_settings(self, file_path='', mapping_key=None):
        """
        Reading yaml files
        :param file_path: str, path
        :param mapping_key: str
        :return: Updates attributes of self
        """
        mapping_file = readers.YAMLreader().load_yaml(file_path, return_config=True)
        if mapping_key:
            mapping_file = mapping_file[mapping_key]
        
        self.add_entries(**mapping_file)

    def map_parameter_list(self, para_list, ext_list=False):
        """
        Map parameters to parameter mapping
        :param para_list: list of parameters
        :param ext_list: False or True, NotImplemented
        :return: list of mapped parameter names
        """
        return self.get_list(para_list)

    def get_parameter_mapping(self, para_list, ext_list=False):
        """
        :param para_list: list of parameters
        :param ext_list: False or True, NotImplemented
        :return: Dictionary
        """
        return self.get_mapping_dict(para_list)


"""
#==============================================================================
#==============================================================================
"""


class ShipMapping(AttributeDict):
    """ Load file to map 2sign-cntry and 2sign-shipc to 4sign-shipc (ICES / SMHI)
    """
    def __init__(self):
        super().__init__()

    def load_mapping_settings(self, cntry_head=u'land', ship_head=u'SMHI-kod', to_key=u'kodlista',
                              file_path=u'D:/Utveckling/w_sharktoolbox/SharkToolbox/data/mapping_ship.txt',
                              sep='\t',encoding='cp1252'):
        """
        #TODO fix path to ship mapping file.. There are many files to choose from..
        Reading csv/txt files
        :param cntry_head: str
        :param ship_head: str
        :param to_key: str
        :param file_path: str
        :param sep: str
        :param encoding: str
        :return:
        """
        mapping_file = readers.YAMLreader().load_yaml(file_path, return_config=True)
                                
        self.set_attr_from_keylist(mapping_file, 
                                   from_keys=[cntry_head, ship_head], 
                                   to_key=to_key)

    def map_cntry_and_shipc(self, cntry=None, shipc=None):
        """
        :param cntry: str
        :param shipc: str
        :return: str, SHIP code (according to standard of ICES)
        """
        return self.get(cntry+shipc)

    def map_shipc(self, cntry_shipc):
        """
        :param cntry_shipc: str
        :return: str, SHIP code (according to standard of ICES)
        """
        return self.get(cntry_shipc)


"""
#==============================================================================
#==============================================================================
""" 



























