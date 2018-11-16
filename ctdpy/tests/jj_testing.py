# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 08:22:21 2018

@author: a002028
"""
import sys
import os
current_path = os.path.dirname(os.path.realpath(__file__))[:-5]
sys.path.append(current_path)
sys.path.append("..")
import core
import numpy as np 
import pandas as pd
import yaml
#import core
import config
# from config import recursive_dict_update

# from .config import settings
from core import utils
# from core import readers
# #from core import writers
# from core import mapping
# from core.readers import CNVSeaBird
# import mapping
# from core import template
# from core.readers import load_excel
#
# from core.readers import YAMLreader
# from core.template import Template
import pprint
import time
#==============================================================================
def load_txt_with_pandas(f_name=u'',
                         seperator=u'\t', 
                         header_row=0):
    """ Just an example.. """
    print('Loading text file:', f_name)
    return pd.read_csv(f_name, 
                       sep=seperator, 
                       header=header_row)

#==============================================================================
#def get_index(data, string):
#    return np.where(data.str.startswith(string))[0]

#==============================================================================
#def match_file_pattern():
    
#==============================================================================
#export_path = u'//winfs-proj/proj/havgem/Johannes_Johansson/Datavärdskap/ctdpy/exports/'
#ex_file = u'//winfs-proj/proj/havgem/Johannes_Johansson/Datavärdskap/ctdpy/tests/etc/SBE09_1044_20171113_1254_34_07_0042.cnv'
#data_dir = u'//winfs-proj/proj/havgem/Johannes_Johansson/Datavärdskap/ctdpy/tests/etc/data/'
#template_path = u'//winfs-proj/proj/havgem/Johannes_Johansson/Datavärdskap/ctdpy/templates/Format Physical and chemical.xlsx'
#settings_path = u'//winfs-proj/proj/havgem/Johannes_Johansson/Datavärdskap/ctdpy/core/etc/'

export_path = u'D:/ctdpy/ctdpy/exports/'
ex_file = u'D:/ctdpy/ctdpy/tests/etc/SBE09_1044_20171113_1254_34_07_0042.cnv'
data_dir = u'D:/ctdpy/ctdpy/tests/etc/data/'
template_path = u'D:/ctdpy/ctdpy/templates/Format Physical and chemical.xlsx'
settings_path = u'D:/Utveckling/Github/ctdpy/ctdpy/core/etc/'

para_mapping = settings_path+u'mapping_parameter.yaml'
path_sb_smhi = settings_path+u'seabird_smhi.yaml'
path_disc_depth = settings_path+u'destrete_depths.yaml'
settings_file = settings_path+u'settings_paths.yaml'
#pmap = mapping.ParameterMapping()
#pmap.load_mapping_settings(file_path=para_mapping, mapping_key='parameter_mapping')
#pmap.add_entries(**sb_smhi.get('parameter_mapping'))
#pmap.get_parameter_mapping(['t090C: Temperature [ITS-90, deg C]'])

#sb_smhi = readers.YAMLreader().load_yaml( [path_sb_smhi, para_mapping, path_disc_depth, settings_file], 
#                                          return_config=True )
#sb_smhi = readers.YAMLreader().load_yaml( [settings_file], 
#                                          return_config=True )
#
start_time = time.time()

insettings = config.Settings()
# pprint.pprint(insettings.__dict__.keys())
# pprint.pprint(insettings.readers['seabird_smhi']['reader'].get('reader'))
insettings.set_reader(reader='seabird_smhi')
# pprint.pprint(insettings.__dict__.keys())

utils.set_export_path(export_dir=insettings.settings_paths.get('export_path'))
pprint.pprint(insettings.datasets)
#cnv_sb = CNVSeaBird(insettings)
#cnv_sb.get_data(file_directory=insettings.settings_paths.get('example_data'))
#cnv_sb.merge_data()
##cnv_sb.convert_formats()
#cnv_sb.export_to_template(save_path=insettings.settings_paths.get('export')+u'data.xlsx', 
#                          sheet_name='Data')
print("--%.3f sec" % (time.time() - start_time))

#os.listdir(u'//winfs-proj/proj/havgem/Johannes_Johansson/Datavärdskap/ctdpy/templates')
#start_time = time.time()
#h.translate(maketrans("N"," "), 'xm').replace(' ','')
##re.sub('[N ]', '', h)
#print("--%.15f sec" % (time.time() - start_time))

#path = u'//winfs-proj/proj/havgem/Johannes_Johansson/Datavärdskap/CTD/core/writers'
#pprint.pprint( os.listdir(path) )
#lista = sorted(os.listdir(path))

#==============================================================================


#df = load_excel(f_name=template_path, sheetname='Kolumner', header_row=2)
#t = Template(df)


##
#settings_paths = {u'settings_paths':{u'mapping_parameter': u'/core/etc/mapping_parameter.yaml',
#                  u'destrete_depths': u'/core/etc/destrete_depths.yaml',
#                  u'seabird_smhi': u'/core/etc/seabird_smhi.yaml',
#                  u'template_parameters': u'/core/etc/template_parameters.yaml',
#                  u'template': u'/templates/Format Physical and chemical.xlsx',
#                  u'example_data_path':u'tests/etc/data/',
#                  u'export_path':u'/export/'}}
#map_dict = {key:list(pmap[key]) for key in pmap.keys()}
#settings_paths = {unicode(key, 'cp1252'):unicode(settings_paths[key], 'cp1252') for key in settings_paths.keys()}
#settings_paths = {'settings_paths':settings_paths}
#print yaml.dump(map_dict,default_flow_style=False)#, outfile)
#with open('paths.yaml', 'w') as outfile:
#    yaml.safe_dump(settings_paths, outfile, default_flow_style=True)



#==============================================================================




#hires_dep = cnv_sb.data_dict[u'SBE09_1044_20171113_1254_34_07_0042.cnv']['hires_data'][u'prDM: Pressure, Digiquartz [db]']
#hires_dep = hires_dep.values.astype(float)
#disc_dep = sb_smhi['depths']
#idx = [(np.abs(hires_dep-value)).argmin() for value in disc_dep if value <= hires_dep.max()]
#maxdep_idx = np.where(hires_dep==hires_dep.max())[0][0]
#idx.append( maxdep_idx )
#cnv_sb.reader_path_name
#a = core.readers.yaml_reader.YAMLreader
#h = {'a':[2],'g':[5]}
#h = pd.DataFrame(h)



#data = np.loadtxt(ex_file)
#data = pd.read_csv(ex_file, sep='delimiter')
#
#data = load_txt_with_pandas( f_name= ex_file)
#pdh = readers.SeriesHandler(sb_smhi['datasets']['cnv'])
#s = pdh.get_series_object(data)
#h = pdh.get_data_header(s)
#idx_data = pdh.get_index(s, sb_smhi['datasets']['cnv'].get('identifier_data'))
#df = pd.DataFrame( s[idx_data].str.split().tolist(), columns=h )





#==============================================================================
#==============================================================================
#==============================================================================



#
#depths = {'depths':map(str, [1,5,10,15,20,25,30,40,50,60,70,75,80,90,100,125,150,175,200,225,240,250,300,400,440])}
#depths = pd.DataFrame(depths)
#idx = depths['depths']=='1'
#depths['depths'] = depths['depths'].astype(str)
#with open(u'depths.yaml', 'w') as outfile:
#    yaml.dump(depths, outfile, default_flow_style=False) #, default_flow_style=False)#, default_flow_style=False)

#data = load_txt_with_pandas(f_name=ex_file)
#reader_settings = {'sep':'delimiter', 
#                   'engine':'python'}
#fh = FileHandler()
#data = fh.load_cnv(f_name=ex_file, **reader_settings)
#data = pd.Series( data=data[data.keys()[0]] )
#
#idx = get_index(data, '*END*')
#
#row = data[idx[0]+1].split()
#reader_settings = {'sep':'\t','header':0}
#                   'engine':'python'}
#pmap = fh.load_txt(file_path=para_mapping, sep='\t', encoding='cp1252', fill_nan=u'')
#
#map_dict = {key:list(pmap[key]) for key in pmap.keys()}
#map_dict = {unicode(key, 'cp1252'):[unicode(v, 'cp1252') for v in map_dict[key]] for key in map_dict.keys()}

#print yaml.dump(map_dict,default_flow_style=False)#, outfile)
#with open(para_mapping, 'w') as outfile:
#    yaml.safe_dump(pmap.mapping_file, outfile)#, default_flow_style=False)


#with open('data.yaml') as fd:
#    config = yaml.load(fd)
#template_para = {'template_parameters':['CNDC_CTD', 'DEPH', 'DOXY_CTD', 'FLUO_CTD', 'PRES_CTD', 'SALT_CTD', 'TEMP_CTD']}
#with open(u'template_para.yaml', 'w') as outfile:
#    yaml.dump(template_para, outfile, default_flow_style=False) #, default_flow_style=False)#, default_flow_style=False)


#==============================================================================










