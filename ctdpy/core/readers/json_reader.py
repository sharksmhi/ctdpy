# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 08:46:00 2018

@author: a002028
"""
import json
import numpy as np
import pandas as pd
from ctdpy.core import utils
#from config import recursive_dict_update
# import config
# import sys
# import importlib
# importlib.reload(sys)
# sys.setdefaultencoding('cp1252')


class JSONreader(object):
    """
    - Import json
    - Export to json
    - Find dictionary within json file based on a specific key 
    - Add elements to dictionary
    - Fill up json/dictionary structure with relevant/desired information
    """
    def __init__(self):
        super().__init__()
        # super(JSONreader, self).__init__()
        
        self.config = {}
        
    def _export_json(self, data_dict={}, out_source='', indent=4):
        """ """
        if isinstance(data_dict, pd.DataFrame):
            data_dict = self._get_dict(df=data_dict)
                
        with open(out_source, "w") as outfile:
            json.dump(data_dict, outfile, indent=indent)
            
    def _initiate_attributes(self):
        """ """
        pass
        
    def _initiate_outfile(self):
        """ json files can save multiple dictionaries stored in a list
        """
        self.out_file = []
    
    def _get_dictionary_reference(self, dictionary={}, dict_path=[]):
        """ """
        for key in dict_path:
            if isinstance(key, str) and key not in dictionary:
                return None
            dictionary = dictionary[key]
        return dictionary
            
    def add_element(self, main_key='', label='', value='', dict_path=None, add_dict={}):
        """ main_key: 
            label: 
            value: 
            dict_path: list with a direct path to target key. Ex. ['info','types', 0, 'label']
        """
        if main_key and self.config.get(main_key) is not None:
            return
        
        if dict_path is not None:
            ref = self._get_dictionary_reference(dictionary=self.config,
                                                 dict_path=dict_path)
        
    def append_dict_to_outfile(self, dictionary=None):
        """ Append dict to out_file (list)
            Not necessary if we only want to save 
        """
        
        if not hasattr(self, 'out_file'):
            self._initiate_outfile()
            
        self.out_file.append(dictionary)
        
    def export(self, out_source='', out_file=None):
        """ """
        
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

    def get_dict(self, key=None):
        """ Find a dictionary based on a specific key within the target dictionary
            config could potentially be a list with dictionaries within 
        """
        
        if isinstance(self.config, list):
            for element in self.config:
                if key in element:
                    return element.get(key)
            return None
            
        elif isinstance(self.config, dict):
            return self.json_file.get(key)
                
        else:
            raise UserWarning('The intended use of a json file has an unrecognizable format', 
                              type(self.config))

    def find_key(self, key, dictionary):
        """ Generator to find an element of a specific key.
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
                            
    def load_json(self, config_files=[], return_config=False):
        """ array will be either a list of dictionaries or one single dictionary 
            depending on what the json file includes
        """
        if not isinstance(config_files, (list, np.ndarray)):
            config_files = [config_files]
            
        for config_file in config_files:
            with open(config_file, 'r') as fd:
                self.config = utils.recursive_dict_update(self.config, json.load(fd))

        if return_config:
            return self.config
    
    def setup_dict(self, keys=[]):
        """ """
        return {key:True for key in keys}
                    
    def update_element(self, main_key='', label='', value=''):
        """ """
        pass
