# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 08:22:21 2018

@author: a002028
"""
import sys
sys.path.append('C:\\Utveckling\\sharkpylib')
import time
from pprint import pprint
from ctdpy.core.session import Session
from ctdpy.core import config, data_handlers
from ctdpy.core.writers.profile_plot import ProfilePlot, QCWorkTool
from ctdpy.core.archive_handler import Archive
from sharkpylib.qc.qc_default import QCBlueprint
from ctdpy.core.utils import get_file_list_based_on_suffix, generate_filepaths, get_reversed_dictionary, match_filenames


# base_dir = 'C:\\Utveckling\\ctdpy\\ctdpy\\tests\\etc\\data_aranda'
# base_dir = '\\\\winfs-proj\\proj\\havgem\\EXPRAPP\\Exprap2020\Svea v2-3\\ctd\\data'
# base_dir = '\\\\winfs-proj\\proj\\havgem\\EXPRAPP\\Exprap2020\Svea v6-7 Feb\\ctd\\cnv'
# base_dir = 'C:\\Utveckling\\ctdpy\\ctdpy\\tests\\etc\\exprapp_feb_2020'
# base_dir = 'C:\\Utveckling\\ctdpy\\ctdpy\\tests\\etc\\exprapp_april_2020'
# base_dir = 'C:\\Utveckling\\ctdpy\\ctdpy\\tests\\etc\\ctd_std_fmt_expedition_april_2020'
# base_dir = 'C:\\Utveckling\\ctdpy\\ctdpy\\tests\\etc\\ctd_std_fmt_QC_done_exprapp_april_2020'

# base_dir = 'C:\\Utveckling\\ctdpy\\ctdpy\\exports\\20200304_152042'
# base_dir = 'C:\\Temp\\CTD_DV\\SMHI_2018\\resultat\\archive_20191121_122431\\processed_data'
# base_dir = 'C:\\Temp\\CTD_DV\\SMF_2018\\original'
# base_dir = 'C:\\Temp\\CTD_DV\\SMHI_2018\\original'
# base_dir = 'C:\\Utveckling\\ctdpy\\ctdpy\\tests\\etc\\datatest_CTD_Umeå'
# base_dir = 'C:\\Temp\\CTD_DV\\UMF_2018\\arbetsmapp'
# base_dir = 'C:\\Utveckling\\ctdpy\\ctdpy\\exports\\archive_20200312_132344\\processed_data'
# base_dir = '\\\\WINFS\prod\\shark_bio\\Originalfiler_från_dataleverantörer\\Profil\\NATIONELLA_Data\\2019\\BAS_UMSC\\arbetsmapp\\'
base_dir = '\\\\WINFS\prod\\shark_bio\\Originalfiler_från_dataleverantörer\\Profil\\NATIONELLA_Data\\2018\\BAS_DEEP\\original\\'
# base_dir = 'C:\\Utveckling\\ctdpy\\ctdpy\\exports\\archive_20200326_115716\\processed_data'  # 2019 UMF data

# files = os.listdir(base_dir)
files = generate_filepaths(base_dir,
                           pattern_list=['.TOB', '.xlsx'],
                           # pattern_list=['.cnv', '.xlsx'],
                           # endswith='.cnv',
                           # endswith='.txt',
                           # only_from_dir=False,
                           )

start_time = time.time()
s = Session(filepaths=files,
            reader='deep',
            # reader='smhi',
            # reader='umsc',
            # reader='ctd_stdfmt',
            )
print("Session--%.3f sec" % (time.time() - start_time))
#  -----------------------------------------------------------------------------------------------------------------
#  ###################        TEST PRINTS        ###################
# print('SHIPmapping test', s.settings.smap.map_cntry_and_shipc(cntry='34', shipc='AR'))
# print('SHIPmapping test', s.settings.smap.map_shipc('3401'))
# print('SHIPmapping test', s.settings.smap.map_shipc('Aranda'))
# print('SHIPmapping test', s.settings.smap.map_shipc('ARANDA'))
# pprint(s.settings.templates['ctd_metadata'])
# pprint(s.settings.settings_paths)

#  -----------------------------------------------------------------------------------------------------------------
#  ###################        READ DELIVERY DATA, CNV, XLSX        ###################
start_time = time.time()
# # FIXME "datasets[0]" the list should me merged before given from session.read(add_merged_data=True)
# datasets = s.read(add_merged_data=True, add_low_resolution_data=True)
# datasets = s.read(add_merged_data=True)
datasets = s.read()
# print("Datasets loaded--%.3f sec" % (time.time() - start_time))
# try:
#     pprint(list(datasets[1].keys()))
# except:
#     pass
# pprint(list(datasets[0].keys()))
#  -----------------------------------------------------------------------------------------------------------------
#  ##################        UNIT CONVERSION       ###################
# converter = data_handlers.UnitConverter(s.settings.mapping_unit,
#                                         s.settings.user)
#
# for data_key, item in datasets[0].items():
#     print(data_key)
#     converter.update_meta(item['metadata'])
#     unit_converted = False
#     for parameter in converter.mapper:
#         if parameter in item['data']:
#             unit_converted = True
#             converter.convert_values(item['data'][parameter])
#
#     if unit_converted:
#         converter.rename_dataframe_columns(df=item['data'])
#         converter.append_conversion_comment()


#  -----------------------------------------------------------------------------------------------------------------
#  ##################        QUALITY CONTROL       ###################
# ex_data = datasets[0]['SBE09_1387_20200107_2137_77_10_0006.cnv'].get('hires_data')
# for key in ex_data:
#     if not key.startswith('Q_'):
#         ex_data['Q0_'+key] = ['0000'] * ex_data.__len__()
# pmap = s.settings.pmap

# start_time = time.time()
# for data_key, item in datasets[0].items():
#     print(data_key)
#     parameter_mapping = get_reversed_dictionary(s.settings.pmap, item['data'].keys())
#     qc_run = QCBlueprint(item, parameter_mapping=parameter_mapping)
#     qc_run()
#
# print("QCBlueprint run--%.3f sec" % (time.time() - start_time))
# diff_func = DataDiff(ex_data, parameters=['TEMP_CTD', 'TEMP2_CTD'], acceptable_error=0.5)
# diff_func = DataDiff(ex_data, parameters=['SALT_CTD', 'SALT2_CTD'], acceptable_error=0.3)
# diff_func = func(ex_data, parameters=['CNDC_CTD', 'CNDC2_CTD'], acceptable_error=0.01)
# diff_func = DataDiff(ex_data, parameters=['DOXY_CTD', 'DOXY2_CTD'], acceptable_error=0.3)
# diff_func = DataDiff(ex_data, parameters=['DENS_CTD', 'DENS2_CTD'], acceptable_error=0.3)
# diff_func()
#  -----------------------------------------------------------------------------------------------------------------
#  ##################        SAVE DATA ACCORDING TO CTD TEMPLATE (TXT-FORMAT)        ###################
# start_time = time.time()
# data_path = s.save_data(datasets, writer='ctd_standard_template', return_data_path=True)
# print("Datasets saved--%.3f sec" % (time.time() - start_time))

#  -----------------------------------------------------------------------------------------------------------------
#  ###################        CREATE ARCHIVE        ###################
# start_time = time.time()
# s.create_archive(data_path=data_path)
# print("Archive created--%.3f sec" % (time.time() - start_time))

#  -----------------------------------------------------------------------------------------------------------------
#  ###################        TEST PRINTS        ###################
# from calculator import Calculator
# import numpy as np
# attr_dict = {'latitude': datasets[0]['SBE09_1044_20181205_1536_34_01_0154.cnv']['metadata']['LATIT'],
#              'pressure': datasets[0]['SBE09_1044_20181205_1536_34_01_0154.cnv']['hires_data']['PRES_CTD'].astype(np.float),
#              'gravity': datasets[0]['SBE09_1044_20181205_1536_34_01_0154.cnv']['hires_data']['PRES_CTD'].astype(np.float),
#              'density': datasets[0]['SBE09_1044_20181205_1536_34_01_0154.cnv']['hires_data']['DENS_CTD'].astype(np.float)}
# calc_obj = Calculator()
# td = calc_obj.get_true_depth(attribute_dictionary=attr_dict)
# res_head = 'hires_data'
# res_head = 'lores_data_all'
# print(datasets[0].keys())
# print(datasets[1].keys())
# print(datasets[1]['CTD Profile ifylld.xlsx']['Metadata'].keys())
# print(datasets[0]['SBE09_1044_20181205_1536_34_01_0154.cnv'].keys())
# print(datasets[0]['SBE09_1044_20181205_1536_34_01_0154.cnv']['metadata'].keys())
# print(datasets[0]['SBE09_1044_20181205_1536_34_01_0154.cnv'][res_head].keys())
# pprint(datasets[0].keys())
# print(datasets[0]['SBE09_1044_20181205_1536_34_01_0154.cnv']['metadata']['FILENAME'])
#  -----------------------------------------------------------------------------------------------------------------
#  ###################        WRITE METADATA TO TEMPLATE        ###################
# start_time = time.time()
# s.save_data(datasets[0], writer='metadata_template')
# print("Metadata file created--%.3f sec" % (time.time() - start_time))

#  -----------------------------------------------------------------------------------------------------------------
# TODO läsare med alt. för fler flagfält
# TODO skrivare med alt. för fler Q-flags-fält per parameter

# pprint(s.settings.templates)
# pprint(s.settings.writers['ctd_standard_template']['writer'])
# pprint(type(datasets[0]['Test_Leveransmall_CTD.xlsx']['Sensorinfo'].columns))
# import pandas as pd
# print(datasets[0]['SBE09_0827_20180120_0910_26_01_0126.cnv']['hires_data']['TEMP_CTD'].values)
# datasets[1]['Test_Leveransmall_CTD.xlsx']['Sensorinfo'].pop('Tabellhuvud:')
# print(datasets[1]['Test_Leveransmall_CTD.xlsx']['Information'])
# f = pd.Series(datasets[1]['Test_Leveransmall_CTD.xlsx']['Sensorinfo'].columns)
# print(f)
# print(f.str.cat(sep='\t'))
# for dset in datasets:
#     print(dset.keys())
# FIXME "datasets[0]" the list should me merged before given from session.read(add_merged_data=True)
# template_data = s.get_data_in_template(datasets[0], writer='xlsx', template='phyche')
# pprint(template_data)
# s.save_data(template_data)

#  -----------------------------------------------------------------------------------------------------------------
#  ###################        Plot HTML map /diagrams        ###################

# data_parameter_list = ['PRES_CTD [dbar]',
#                        'SALT_CTD [psu (PSS-78)]', 'SALT2_CTD [psu (PSS-78)]',
#                        'TEMP_CTD [°C (ITS-90)]', 'TEMP2_CTD [°C (ITS-90)]',
#                        'DOXY_CTD [ml/l]', 'DOXY2_CTD [ml/l]',
#                        ]
# plot_parameters_mapping = {'x1': 'TEMP_CTD [°C (ITS-90)]', 'x1b': 'TEMP2_CTD [°C (ITS-90)]',
#                            'x1_q0': 'Q0_TEMP_CTD', 'x1b_q0': 'Q0_TEMP2_CTD',
#                            'x2': 'SALT_CTD [psu (PSS-78)]', 'x2b': 'SALT2_CTD [psu (PSS-78)]',
#                            'x2_q0': 'Q0_SALT_CTD', 'x2b_q0': 'Q0_SALT2_CTD',
#                            'x3': 'DOXY_CTD [ml/l]', 'x3b': 'DOXY2_CTD [ml/l]',
#                            'x3_q0': 'Q0_DOXY_CTD', 'x3b_q0': 'Q0_DOXY2_CTD',
#                            'y': 'PRES_CTD [dbar]'}
# q_flag_parameters = ['Q_SALT_CTD', 'Q_SALT2_CTD', 'Q_TEMP_CTD', 'Q_TEMP2_CTD', 'Q_DOXY_CTD', 'Q_DOXY2_CTD']
# auto_q_flag_parameters = ['Q0_SALT_CTD', 'Q0_SALT2_CTD', 'Q0_TEMP_CTD', 'Q0_TEMP2_CTD', 'Q0_DOXY_CTD', 'Q0_DOXY2_CTD']
# q_colors = ['color_x1', 'color_x2', 'color_x3', 'color_x1b', 'color_x2b', 'color_x3b']

# data_parameter_list = ['PRES_CTD [dbar]', 'SALT_CTD [psu (PSS-78)]',
#                        'TEMP_CTD [°C (ITS-90)]', 'DOXY_CTD [ml/l]',
#                        ]
# plot_parameters_mapping = {'x1': 'TEMP_CTD [°C (ITS-90)]',
#                            'x1_q0': 'Q0_TEMP_CTD',
#                            'x2': 'SALT_CTD [psu (PSS-78)]',
#                            'x2_q0': 'Q0_SALT_CTD',
#                            'x3': 'DOXY_CTD [ml/l]',
#                            'x3_q0': 'Q0_DOXY_CTD',
#                            'y': 'PRES_CTD [dbar]'}
#
# q_flag_parameters = ['Q_SALT_CTD', 'Q_TEMP_CTD', 'Q_DOXY_CTD']
# auto_q_flag_parameters = ['Q0_SALT_CTD', 'Q0_TEMP_CTD', 'Q0_DOXY_CTD']
# #
# q_colors = ['color_x1', 'color_x2', 'color_x3']
# df_parameter_list = data_parameter_list + q_colors + q_flag_parameters + auto_q_flag_parameters + \
#                     ['STATION', 'LATITUDE_DD', 'LONGITUDE_DD', 'SDATE', 'MONTH', 'STIME', 'KEY']
#
# parameter_formats = {p: float for p in data_parameter_list}
# start_time = time.time()
#
# data_transformer = data_handlers.DataTransformation()
# data_transformer.add_keys_to_datasets(datasets)
#
# dataframes = [datasets[0][key].get('data') for key in datasets[0].keys()]
# data_transformer.append_dataframes(dataframes)
# data_transformer.add_columns()
# data_transformer.add_color_columns(auto_q_flag_parameters)
# data_transformer.set_column_format(**parameter_formats)
#
# dataframe = data_transformer.get_dataframe(columns=df_parameter_list)
#
# print("Data retrieved--%.3f sec" % (time.time() - start_time))
#
# # TODO
# #  - Spara undan datafilerna i txtformat
# #  - Separera data och metadata
# #  - Addera QC_COMNT
#
# start_time = time.time()
# plot = QCWorkTool(dataframe,
#               datasets=datasets[0],
#               parameters=data_parameter_list,
#               plot_parameters_mapping=plot_parameters_mapping,
#               color_fields=q_colors,
#               qflag_fields=q_flag_parameters,
#               auto_q_flag_parameters=auto_q_flag_parameters,
#               output_filename="svea_2020.html",
#               # output_filename="UMSC_2019.html",
#               )
# # plot.set_map()
# plot.plot_stations()
# plot.plot_data()
# plot.show_plot()
# # plot.plot(x='TEMP_CTD [°C (ITS-90)]',
# #              y='PRES_CTD [dbar]',
# #              z='SALT_CTD [psu (PSS-78)]',
# #              name=profile_name)
# print("Data plotted--%.3f sec" % (time.time() - start_time))




# import sys
# import os
# current_path = os.path.dirname(os.path.realpath(__file__))[:-5]
# sys.path.append(current_path)
# sys.path.append("..")
# import core
# import numpy as np
# import pandas as pd
# import yaml
# #import core
# import config
# # from config import recursive_dict_update
#
# # from .config import settings
# from core import utils
# # from core import readers
# # #from core import writers
# # from core import mapping
# # from core.readers import CNVSeaBird
# # import mapping
# # from core import template
# # from core.readers import load_excel
# #
# # from core.readers import YAMLreader
# # from core.template import Template
# import pprint
# import time
# #==============================================================================
# def load_txt_with_pandas(f_name=u'',
#                          seperator=u'\t',
#                          header_row=0):
#     """ Just an example.. """
#     print('Loading text file:', f_name)
#     return pd.read_csv(f_name,
#                        sep=seperator,
#                        header=header_row)
#
# #==============================================================================
# #def get_index(data, string):
# #    return np.where(data.str.startswith(string))[0]
#
# #==============================================================================
# #def match_file_pattern():
#
# #==============================================================================
# #export_path = u'//winfs-proj/proj/havgem/Johannes_Johansson/Datavärdskap/ctdpy/exports/'
# #ex_file = u'//winfs-proj/proj/havgem/Johannes_Johansson/Datavärdskap/ctdpy/tests/etc/SBE09_1044_20171113_1254_34_07_0042.cnv'
# #data_dir = u'//winfs-proj/proj/havgem/Johannes_Johansson/Datavärdskap/ctdpy/tests/etc/data/'
# #template_path = u'//winfs-proj/proj/havgem/Johannes_Johansson/Datavärdskap/ctdpy/templates/Format Physical and chemical.xlsx'
# #settings_path = u'//winfs-proj/proj/havgem/Johannes_Johansson/Datavärdskap/ctdpy/core/etc/'
#
# export_path = u'D:/ctdpy/ctdpy/exports/'
# ex_file = u'D:/ctdpy/ctdpy/tests/etc/SBE09_1044_20171113_1254_34_07_0042.cnv'
# data_dir = u'D:/ctdpy/ctdpy/tests/etc/data/'
# template_path = u'D:/ctdpy/ctdpy/templates/Format Physical and chemical.xlsx'
# settings_path = u'D:/Utveckling/Github/ctdpy/ctdpy/core/etc/'
#
# para_mapping = settings_path+u'mapping_parameter.yaml'
# path_sb_smhi = settings_path+u'seabird_smhi.yaml'
# path_disc_depth = settings_path+u'destrete_depths.yaml'
# settings_file = settings_path+u'settings_paths.yaml'
# #pmap = mapping.ParameterMapping()
# #pmap.load_mapping_settings(file_path=para_mapping, mapping_key='parameter_mapping')
# #pmap.add_entries(**sb_smhi.get('parameter_mapping'))
# #pmap.get_parameter_mapping(['t090C: Temperature [ITS-90, deg C]'])
#
# #sb_smhi = readers.YAMLreader().load_yaml( [path_sb_smhi, para_mapping, path_disc_depth, settings_file],
# #                                          return_config=True )
# #sb_smhi = readers.YAMLreader().load_yaml( [settings_file],
# #                                          return_config=True )
# #
# start_time = time.time()
#
# insettings = config.Settings()
# # pprint.pprint(insettings.__dict__.keys())
# # pprint.pprint(insettings.readers['seabird_smhi']['reader'].get('reader'))
# insettings.set_reader(reader='seabird_smhi')
# # pprint.pprint(insettings.__dict__.keys())
#
# utils.set_export_path(export_dir=insettings.settings_paths.get('export_path'))
# pprint.pprint(insettings.datasets)
# #cnv_sb = CNVSeaBird(insettings)
# #cnv_sb.get_data(file_directory=insettings.settings_paths.get('example_data'))
# #cnv_sb.merge_data()
# ##cnv_sb.convert_formats()
# #cnv_sb.export_to_template(save_path=insettings.settings_paths.get('export')+u'data.xlsx',
# #                          sheet_name='Data')
# print("--%.3f sec" % (time.time() - start_time))
#
# #os.listdir(u'//winfs-proj/proj/havgem/Johannes_Johansson/Datavärdskap/ctdpy/templates')
# #start_time = time.time()
# #h.translate(maketrans("N"," "), 'xm').replace(' ','')
# ##re.sub('[N ]', '', h)
# #print("--%.15f sec" % (time.time() - start_time))
#
# #path = u'//winfs-proj/proj/havgem/Johannes_Johansson/Datavärdskap/CTD/core/writers'
# #pprint.pprint( os.listdir(path) )
# #lista = sorted(os.listdir(path))
#
# #==============================================================================
#
#
# #df = load_excel(f_name=template_path, sheetname='Kolumner', header_row=2)
# #t = Template(df)
#
#
# ##
# #settings_paths = {u'settings_paths':{u'mapping_parameter': u'/core/etc/mapping_parameter.yaml',
# #                  u'destrete_depths': u'/core/etc/destrete_depths.yaml',
# #                  u'seabird_smhi': u'/core/etc/seabird_smhi.yaml',
# #                  u'template_parameters': u'/core/etc/template_parameters.yaml',
# #                  u'template': u'/templates/Format Physical and chemical.xlsx',
# #                  u'example_data_path':u'tests/etc/data/',
# #                  u'export_path':u'/export/'}}
# #map_dict = {key:list(pmap[key]) for key in pmap.keys()}
# #settings_paths = {unicode(key, 'cp1252'):unicode(settings_paths[key], 'cp1252') for key in settings_paths.keys()}
# #settings_paths = {'settings_paths':settings_paths}
# #print yaml.dump(map_dict,default_flow_style=False)#, outfile)
# #with open('paths.yaml', 'w') as outfile:
# #    yaml.safe_dump(settings_paths, outfile, default_flow_style=True)
#
#
#
# #==============================================================================
#
#
#
#
# #hires_dep = cnv_sb.data_dict[u'SBE09_1044_20171113_1254_34_07_0042.cnv']['hires_data'][u'prDM: Pressure, Digiquartz [db]']
# #hires_dep = hires_dep.values.astype(float)
# #disc_dep = sb_smhi['depths']
# #idx = [(np.abs(hires_dep-value)).argmin() for value in disc_dep if value <= hires_dep.max()]
# #maxdep_idx = np.where(hires_dep==hires_dep.max())[0][0]
# #idx.append( maxdep_idx )
# #cnv_sb.reader_path_name
# #a = core.readers.yaml_reader.YAMLreader
# #h = {'a':[2],'g':[5]}
# #h = pd.DataFrame(h)
#
#
#
# #data = np.loadtxt(ex_file)
# #data = pd.read_csv(ex_file, sep='delimiter')
# #
# #data = load_txt_with_pandas( f_name= ex_file)
# #pdh = readers.SeriesHandler(sb_smhi['datasets']['cnv'])
# #s = pdh.get_series_object(data)
# #h = pdh.get_data_header(s)
# #idx_data = pdh.get_index(s, sb_smhi['datasets']['cnv'].get('identifier_data'))
# #df = pd.DataFrame( s[idx_data].str.split().tolist(), columns=h )
#
#
#
#
#
# #==============================================================================
# #==============================================================================
# #==============================================================================
#
#
#
# #
# #depths = {'depths':map(str, [1,5,10,15,20,25,30,40,50,60,70,75,80,90,100,125,150,175,200,225,240,250,300,400,440])}
# #depths = pd.DataFrame(depths)
# #idx = depths['depths']=='1'
# #depths['depths'] = depths['depths'].astype(str)
# #with open(u'depths.yaml', 'w') as outfile:
# #    yaml.dump(depths, outfile, default_flow_style=False) #, default_flow_style=False)#, default_flow_style=False)
#
# #data = load_txt_with_pandas(f_name=ex_file)
# #reader_settings = {'sep':'delimiter',
# #                   'engine':'python'}
# #fh = FileHandler()
# #data = fh.load_cnv(f_name=ex_file, **reader_settings)
# #data = pd.Series( data=data[data.keys()[0]] )
# #
# #idx = get_index(data, '*END*')
# #
# #row = data[idx[0]+1].split()
# #reader_settings = {'sep':'\t','header':0}
# #                   'engine':'python'}
# #pmap = fh.load_txt(file_path=para_mapping, sep='\t', encoding='cp1252', fill_nan=u'')
# #
# #map_dict = {key:list(pmap[key]) for key in pmap.keys()}
# #map_dict = {unicode(key, 'cp1252'):[unicode(v, 'cp1252') for v in map_dict[key]] for key in map_dict.keys()}
#
# #print yaml.dump(map_dict,default_flow_style=False)#, outfile)
# #with open(para_mapping, 'w') as outfile:
# #    yaml.safe_dump(pmap.mapping_file, outfile)#, default_flow_style=False)
#
#
# #with open('data.yaml') as fd:
# #    config = yaml.load(fd)
# #template_para = {'template_parameters':['CNDC_CTD', 'DEPH', 'DOXY_CTD', 'FLUO_CTD', 'PRES_CTD', 'SALT_CTD', 'TEMP_CTD']}
# #with open(u'template_para.yaml', 'w') as outfile:
# #    yaml.dump(template_para, outfile, default_flow_style=False) #, default_flow_style=False)#, default_flow_style=False)
#
#
# #==============================================================================
#
#
#
#
#
#
# ########################################################################################################################
# ################################################       L O G     #######################################################
# ########################################################################################################################
# import logging
# # LOG = logging.getLogger(__name__)
#
#
# # create the logging instance for logging to file only
# # logger = logging.getLogger('SmartfileTest')
#
# # create the handler for the main logger
# # file_logger = logging.FileHandler(__name__)
# # NEW_FORMAT = '[%(asctime)s] - [%(levelname)s] - %(message)s'
# # file_logger_format = logging.Formatter(NEW_FORMAT)
# #
# # # tell the handler to use the above format
# # file_logger.setFormatter(file_logger_format)
# #
# # # finally, add the handler to the base logger
# # LOG.addHandler(file_logger)
# #
# # # remember that by default, logging will start at 'warning' unless
# # # we set it manually
# # LOG.setLevel(logging.DEBUG)
#
# # log some stuff!
# # LOG.debug("This is a debug message!")
# # LOG.info("This is an info message!")
# # LOG.warning("This is a warning message!")
#
# # log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s',
# #                                   datefmt='%d/%m/%Y %H:%M:%S')
# #
# # #File to log to
# # logFile = 'log.txt'
# #
# # #Setup File handler
# # file_handler = logging.FileHandler(logFile)
# # file_handler.setFormatter(log_formatter)
# # file_handler.setLevel(logging.INFO)
# #
# # #Setup Stream Handler (i.e. console)
# # stream_handler = logging.StreamHandler()
# # stream_handler.setFormatter(log_formatter)
# # stream_handler.setLevel(logging.INFO)
# #
# # #Get our logger
# # LOG = logging.getLogger('root')
# # LOG.setLevel(logging.INFO)
# #
# # #Add both Handlers
# # LOG.addHandler(file_handler)
# # LOG.addHandler(stream_handler)
# #
# # # stop propagting to root logger
# # LOG.propagate = False
# #
# # #Write some Data
# # LOG.debug("This is a debug message!")
# # LOG.info("This is an info message!")
# # LOG.warning("This is a warning message!")
# #
# # # missing_str = ", ".join(str(x) for x in missing)
# # LOG.warning(
# #     "The following datasets "
# #     "were not created: {}".format('4,5'))
# ########################################################################################################################
