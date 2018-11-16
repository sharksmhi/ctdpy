# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 08:22:21 2018

@author: a002028
"""
import ctdpy
from ctdpy.core import readers
import pprint
import time
#==============================================================================

# Create Settings object 
insettings = ctdpy.config.Settings()

# pretty print
pprint.pprint( insettings.settings_paths )



start_time = time.time()


# Creates reader object based on data (could be "any" type of sensor data, in 
# "any" kind of format)
cnv_sb = readers.CNVSeaBird( insettings )


# Loading as hi-resolution-, lo-resolution- and meta-data
cnv_sb.get_data( file_directory=insettings.settings_paths.get('example_data') )


# Merging resolution specified data with metadata in dataframe
cnv_sb.merge_data(resolution='lores_data')


#ctdpy3.core.utils.set_export_path(export_dir=insettings.settings_paths.get('export'))


# Save data to datahost template
cnv_sb.export_to_template( save_path=insettings.settings_paths.get('export')+u'data.xlsx', 
                           sheet_name='Data' )
                          
print("--%.3f sec" % (time.time() - start_time))



#==============================================================================






