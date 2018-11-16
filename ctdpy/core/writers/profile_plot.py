# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 13:19:50 2018

@author: a002028
"""

"""
https://groups.google.com/a/continuum.io/forum/#!topic/bokeh/Ts2P24YR0VU

Until 0.11 this was actually the default mode of operation, but folks asked for CDN loading to be the default, so that change was made. But you can still use INLINE resources explicitly you can create self-contained standalone documents. This is available in bokeh.resources: 

        from bokeh.resources import INLINE 

And can be passed to many of the output functions, e.g., file_html: 

        with open(filename, "w") as f: 
                f.write(file_html(doc, INLINE, "Demonstration of inline resources")) 

This creates a standalone HTML document with all data, JS and CSS embedded inside the one file. 

It is also possible to spell this intention another way, by simply passing mode="inline" to output_file (if you are using output_file): 

        output_file(file_path, mode='inline') 

Finally, you could also serve the Bokeh JS and CSS resources yourself on your own server on your internal network, and create documents that load the resources from there. This is a little bit more involved (and I'd have to refresh my memory in some cases) so unless you are interested specifically in this scenario I won't expand further here. 

"""
import numpy as np
import pandas as pd
from pprint import pprint
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.plotting import figure, show, output_file
from bokeh.sampledata.periodic_table import elements
from bokeh.plotting import figure, show, output_file
from bokeh.resources import INLINE

class ProfilePlot(object):
    """
    """
    def __init__(self, settings):
        super(ProfilePlot, self).__init__()
        self.settings = settings

    def plot(self, df, x=None, y=None, z=None, name=''):
        """ """
        TITLE = "Test Profile Plot"
        TOOLS = "hover,pan,wheel_zoom,box_zoom,reset,save"

        p = figure(tools=TOOLS, toolbar_location="above", logo="grey", plot_width=1200, title=TITLE)
        p.background_fill_color = "#dddddd"
        p.xaxis.axis_label = x
        p.yaxis.axis_label = y
        p.grid.grid_line_color = "white"

        source = ColumnDataSource(df)

        p.circle(x, y, size=12, source=source,
                 line_color="black", fill_alpha=0.8)
        # p.line(x, y, source=source, color='#A6CEE3')

        labels = LabelSet(x=x, y=y,
                          text=z,
                          y_offset=8,
                          text_font_size="8pt", text_color="#555555",
                          source=source, text_align='center')
        p.add_layout(labels)

        if name == '':
            name = "profile_plot.html"
        elif not name.endswith('.html'):
            name = name+'.html'
        output_file(name, mode='inline', title=name)
        show(p)

if __name__ == '__main__':
    pass
    #profile = ProfilePlot(s.settings)
    #for fid in datasets[0]:
    #    name = fid.split('/')[-1].replace('.cnv','')
    #    profile.plot(datasets[0][fid]['hires_data'], x='TEMP_CTD', y='PRES_CTD', z='SALT_CTD', name=name)


# file_path = 'D:\\Utveckling\\Github\\ctdpy\\ctdpy\\exports\\data.xlsx'
# df = pd.read_excel(file_path, sheet_name='Data', header_row=0)
# df['PRES_CTD'] = df['PRES_CTD'].apply(lambda x: x*(-1))
# one_profile = df.loc[0:10, :]
# pprint(one_profile['PRES_CTD'])
# # pprint(elements)
# # print(elements.keys())
#
# TITLE = "Test Profile Plot"
# TOOLS = "hover,pan,wheel_zoom,box_zoom,reset,save"
#
# p = figure(tools=TOOLS, toolbar_location="above", logo="grey", plot_width=1200, title=TITLE)
# p.background_fill_color = "#dddddd"
# p.xaxis.axis_label = "TEMP_CTD"
# p.yaxis.axis_label = "PRES_CTD"
# p.grid.grid_line_color = "white"
#
#
# source = ColumnDataSource(one_profile)
#
# p.circle("TEMP_CTD", "SALT_CTD", size=12, source=source,
#          line_color="black", fill_alpha=0.8)
# # p.line("TEMP_CTD", "PRES_CTD", source=source, color='#A6CEE3')
#
# labels = LabelSet(x="TEMP_CTD", y="SALT_CTD",
#                   text="PRES_CTD",
#                   y_offset=8,
#                   text_font_size="8pt", text_color="#555555",
#                   source=source, text_align='center')
# p.add_layout(labels)
#
# output_file("profile_plot.html", mode='inline', title="profile_plot.py example")
#
# show(p)
