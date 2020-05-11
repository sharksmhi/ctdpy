# -*- coding: utf-8 -*-
"""
Created on 2020-05-08 10:36

@author: a002028

"""
import sys
sys.path.append('C:\\Utveckling\\sharkpylib')
sys.path.append('C:\\Utveckling\\ctdpy')  #

from bokeh import __version__
print('bokeh version', __version__)
from bokeh.client import push_session
from bokeh.embed import server_document
from bokeh.plotting import figure, curdoc

from ctdpy.core.session import Session
from ctdpy.core.utils import generate_filepaths, get_reversed_dictionary
from ctdpy.core.data_handlers import DataTransformation
from ctdpy.core.writers.profile_plot import QCWorkTool

import time
from pprint import pprint


def run_data_prep(layout_return=False):
    base_dir = 'C:\\Utveckling\\ctdpy\\ctdpy\\tests\\etc\\ctd_std_fmt_QC_done_exprapp_april_2020'
    files = generate_filepaths(base_dir,
                               endswith='.txt',  # Presumably CTD-standard format
                               only_from_dir=True,
                               )

    s = Session(filepaths=files,
                reader='ctd_stdfmt',
                )

    start_time = time.time()
    datasets = s.read()
    print("Datasets loaded--%.3f sec" % (time.time() - start_time))

    para_list = [p for p in datasets[0]['ctd_profile_20200417_77SE_0353.txt']['data'].columns if
                 ('[' in p and not p.startswith('DEPH') and not p.startswith('PRES'))]

    data_parameter_list = ['TEMP_CTD [°C (ITS-90)]', 'SALT_CTD [psu (PSS-78)]', 'DOXY_CTD [ml/l]',
                           'TEMP2_CTD [°C (ITS-90)]', 'SALT2_CTD [psu (PSS-78)]', 'DOXY2_CTD [ml/l]',
                           'CNDC_CTD [S/m]', 'PAR_CTD [µE/(cm2 sec)]', 'CHLFLUO_CTD [mg/m3]', 'PHYC_CTD [ppb]', 'TURB_CTD [NTU]']
    q_flag_parameters = []
    auto_q_flag_parameters = []
    q_colors = []
    q_colors_mapper = {}

    plot_parameters_mapping = {'y': 'PRES_CTD [dbar]'}
    for i, p in enumerate(data_parameter_list):
        x_key = 'x' + str(i + 1)
        q0x_key = x_key + '_q0'
        parameter = p.split()[0]
        c_para = 'color_' + x_key
        q_para = 'Q_' + parameter
        q0_para = 'Q0_' + parameter

        q_colors.append(c_para)
        q_flag_parameters.append(q_para)
        auto_q_flag_parameters.append(q0_para)

        q_colors_mapper[q0_para] = c_para
        plot_parameters_mapping[x_key] = p
        plot_parameters_mapping[q0x_key] = q0_para

    data_parameter_list.append('PRES_CTD [dbar]')
    df_parameter_list = data_parameter_list + q_colors + q_flag_parameters + auto_q_flag_parameters + \
                        ['STATION', 'LATITUDE_DD', 'LONGITUDE_DD', 'SDATE', 'MONTH', 'STIME', 'KEY']

    parameter_formats = {p: float for p in data_parameter_list}

    start_time = time.time()

    data_transformer = DataTransformation()
    data_transformer.add_keys_to_datasets(datasets)

    dataframes = [datasets[0][key].get('data') for key in datasets[0].keys()]
    data_transformer.append_dataframes(dataframes)
    data_transformer.add_columns()
    data_transformer.add_color_columns(auto_q_flag_parameters, mapper=q_colors_mapper)
    data_transformer.set_column_format(**parameter_formats)

    dataframe = data_transformer.get_dataframe(columns=df_parameter_list)
    print("Data retrieved--%.3f sec" % (time.time() - start_time))

    # start_time = time.time()
    plot = QCWorkTool(dataframe,
                      datasets[0],
                      parameters=data_parameter_list,
                      plot_parameters_mapping=plot_parameters_mapping,
                      color_fields=q_colors,
                      qflag_fields=q_flag_parameters,
                      auto_q_flag_parameters=auto_q_flag_parameters,
                      #               output_filename="svea_2020.html",                     # Save as html-file (will automatic open in chrome/firefox), only javascript callbacks can be used
                      output_as_notebook=True,
                      # Open in notebook.. Window size is not ideal for this, BUT! python callbacks works :D
                      ctdpy_session=s,
                      multi_sensors=True,
                      )
    plot.plot_stations()
    plot.plot_data()

    if layout_return:
        bk_layout = plot.return_layout()
        return bk_layout


"""
https://stackoverflow.com/questions/55049175/running-bokeh-server-on-local-network

bokeh serve app_to_serve.py

Open in web browser: http://localhost:5006/run_bokeh_server.
"""
# if __name__ == '__main__':
bokeh_layout = run_data_prep(layout_return=True)
doc = curdoc()
doc.add_root(bokeh_layout)
