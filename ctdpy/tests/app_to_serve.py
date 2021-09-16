# -*- coding: utf-8 -*-
"""
Created on 2020-05-08 10:36

@author: a002028


Ref: https://stackoverflow.com/questions/55049175/running-bokeh-server-on-local-network

In a conda-prompt run:
    cd "PATH_TO_THIS_SCRIPT"
    bokeh serve app_to_serve.py

Open in web browser: http://localhost:5006/app_to_serve
    Bokeh app running at: http://localhost:5006/app_to_serve

"""
import sys
# sys.path.append('C:\\Utveckling\\ctdvis')
from bokeh.plotting import curdoc
from ctdvis.session import Session


def bokeh_qc_tool():
    # data_dir = r'C:\mw\temp_svea\standard_format'
    # data_dir = r'C:\mw\Profile\2018\SHARK_Profile_2018_BAS_SMHI\processed_data'
    # data_dir = 'C:\\Temp\\CTD_DV\\qc_SMHI_2018\\ctd_std_fmt_20200622_130128_april_2020'
    # data_dir = 'C:\\Temp\\CTD_DV\\qc_SMHI_2018\\ctd_std_fmt_20200622_130128_april_2020'
    # data_dir = 'C:/Arbetsmapp/datasets/Profile/2019/SHARK_Profile_2019_SMHI/processed_data'
    # data_dir = 'C:\\Arbetsmapp\\datasets\\Profile\\2018\\SHARK_Profile_2018_BAS_SMHI\\processed_data'

    """ Filters are advised to be implemented if the datasource is big, (~ >3 months of SMHI-EXP-data) """
    # filters = None
    filters = dict(
        month_list=[5],
        # month_list=[1, 2, 3],
        # month_list=[4, 5, 6],
        # month_list=[7, 8, 9],
        # month_list=[10, 11, 12],
        # ship_list=['77SE', '34AR']
        # serno_min=311,
        # serno_max=355,
    )

    s = Session(visualize_setting='smhi_vis', data_directory=data_dir, filters=filters)
    s.setup_datahandler()
    layout = s.run_tool(return_layout=True)

    return layout


bokeh_layout = bokeh_qc_tool()
doc = curdoc()
doc.add_root(bokeh_layout)
