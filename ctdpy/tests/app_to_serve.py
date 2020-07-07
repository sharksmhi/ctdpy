# -*- coding: utf-8 -*-
"""
Created on 2020-05-08 10:36

@author: a002028

"""
import sys
sys.path.append('C:\\Utveckling\\ctdvis')  # Append local path to our python repository "ctdvis"

from bokeh import __version__
print('bokeh version: {}'.format(__version__))

from bokeh.plotting import curdoc
from ctdvis.session import Session


def bokeh_qc_tool():

    data_dir = 'C:\\Temp\\CTD_DV\\qc_SMHI_2018\\ctd_std_fmt_20200622_130128_april_2020'

    s = Session(visualize_setting='smhi_vis', data_directory=data_dir)
    s.setup_datahandler()
    layout = s.run_tool(return_layout=True)

    return layout


"""
https://stackoverflow.com/questions/55049175/running-bokeh-server-on-local-network

bokeh serve app_to_serve.py

Open in web browser: http://localhost:5006/run_bokeh_server.
"""
# if __name__ == '__main__':
bokeh_layout = bokeh_qc_tool()
doc = curdoc()
doc.add_root(bokeh_layout)
