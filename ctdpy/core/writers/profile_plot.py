# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 13:19:50 2018

@author: a002028
"""

import time
from functools import partial
import numpy as np
import pandas as pd
import zipfile
# from pprint import pprint
from bokeh.io import output_notebook
from bokeh.models import Button, FileInput, TextInput, ColumnDataSource, Range1d, CustomJS, Div, WidgetBox, LinearAxis, Circle, TapTool, HoverTool, CrosshairTool, WheelZoomTool, ResetTool, PanTool, SaveTool,  LassoSelectTool, ColorBar, LinearColorMapper  # , LabelSet, Slider
from bokeh.layouts import grid, row, column, layout, gridplot, GridSpec, widgetbox, Spacer  # , layout, widgetbox
from bokeh.models.widgets import Select, RangeSlider, DataTable, TableColumn, Panel, Tabs
from bokeh.plotting import figure, show, output_file
from bokeh.tile_providers import get_provider, Vendors
from bokeh.events import ButtonClick
from bokeh.palettes import viridis   #  magma, viridis
from matplotlib import colors
from matplotlib import cm
import gsw

from ctdpy.core.utils import get_time_as_format
# import panel as pn
# pn.extension()


def get_contour_arrays(x_min, x_max, y_min, y_max):
    """
    Calculate how many gridcells we need in the x and y dimensions
    Assuming x_key = Salinity and y_key = Temperature
    :return:
    """
    xdim = int(round((x_max - x_min) / 0.1 + 1, 0))
    ydim = int(round((y_max - y_min) / 0.1 + 1, 0))
    t_m = np.zeros((ydim, xdim))
    s_m = np.zeros((ydim, xdim))
    dens = np.zeros((ydim, xdim))
    ti = np.linspace(1, ydim - 1, ydim) * 0.1 + y_min
    si = np.linspace(1, xdim - 1, xdim) * 0.1 + x_min
    for j in range(0, int(ydim)):
        for i in range(0, int(xdim)):
            dens[j, i] = gsw.rho(si[i], ti[j], 0)
            s_m[j, i] = si[i]
            t_m[j, i] = ti[j]
    dens = dens
    return dens, t_m, s_m


def get_contour_data(x_min, x_max, y_min, y_max):
    """
    Example:
    x_min, x_max, y_min, y_max = 0, 40, -10, 30
    data = get_contour_df(x_min, x_max, y_min, y_max)
    """
    dens, t_m, s_m = get_contour_arrays(x_min, x_max, y_min, y_max)
    dens = np.round(dens, 2)
    data = {}
    selected_densities = np.arange(-6, 31, 2) + 1000
    for s_dens in selected_densities:
        # print('Selected density: {}'.format(s_dens))
        index = dens == s_dens
        data[str(s_dens)] = {'temp': t_m[index],
                             'salt': s_m[index],
                             'dens': dens[index]}
    return data


def get_color_palette(dep_serie=None, ):
    number_of_colors = int(dep_serie.max()) * 2 + 1
    # cm_map = cm.get_cmap('viridis', number_of_colors)
    cm_map = cm.get_cmap('cool', number_of_colors)
    color_array = pd.Series([colors.to_hex(cm_map(c)) for c in range(number_of_colors)])

    return [color_array[int(d*2)] if d > 0 else 0 for d in dep_serie]


def convert_projection(lats, lons):
    """

    :param lats:
    :param lons:
    :return:
    """
    #TODO MOVE! this exists somewhere else too..
    import pyproj

    # project_projection = pyproj.Proj("EPSG:4326")  # wgs84
    # google_projection = pyproj.Proj("EPSG:3857")  # default google projection
    project_projection = pyproj.Proj({'init': 'epsg:4326', 'no_defs': True}, preserve_flags=True)  # wgs84
    google_projection = pyproj.Proj({'init': 'epsg:3857', 'no_defs': True}, preserve_flags=True)  # default google projection

    x, y = pyproj.transform(project_projection, google_projection, lons, lats)
    return x, y


class ReadZipFile(object):
    """
    """
    def __init__(self, zipfile_path, filename):

        self.archive = zipfile.ZipFile(zipfile_path, 'r')

        try:
            file_path = self.get_filepath(self.archive.namelist(), filename)
            row_list = self.open_file(file_path)
        except IOError:
            raise IOError("{} not found in {}".format(filename, zipfile_path))

        self.setup_dataframe(row_list)

    def setup_dataframe(self, row_list, sep='\t'):
        """
        Creates pd.Series with row_list as input
        :param row_list: list of rows
        :param sep: str, splits each row
        :return: pd.DataFrame
        """
        serie = pd.Series(data=row_list)
        columns = serie.iloc[0].split(sep)
        bool_array = serie.index > 0
        self._df = pd.DataFrame(serie.iloc[bool_array].str.split(sep).tolist(),
                                columns=columns)
        self._df.replace('', np.nan, inplace=True)

    def get_dataframe(self):
        """
        :return: pd.DataFrame
        """
        return self._df

    def get_data(self, parameters, astype=np.float):
        """
        :param parameters: list, all parameters to include in return
        :param astype: set data as this type eg. float, int, str
        :return: dict or pd.DataFrame
        """
        if astype:
            return self._df.loc[:, parameters].astype(astype)
        else:
            return self._df.loc[:, parameters]

    def open_file(self, file_path, comment='//'):
        """
        :param file_path: str, path to file
        :param comment: str, exclude rows that starts with this comment
        :return: list, selected rows
        """
        file = self.archive.open(file_path)
        row_list = [l.decode('cp1252') for l in file if not l.decode('cp1252').startswith(comment)]

        return row_list

    @staticmethod
    def get_filepath(path_list, pattern):
        """
        :param path_list:
        :param pattern:
        :return:
        """
        for path in path_list:
            if pattern in path:
                return path


class BaseAxes(object):
    """
    """
    def __init__(self):
        self._xaxis = None
        self._yaxis = None

    def _convert_yaxis_values(self, y):
        """
        Requires derived classes to override this method
        """
        raise NotImplementedError

    @property
    def xaxis(self):
        """
        :return: xaxis
        """
        return self._xaxis

    @xaxis.setter
    def xaxis(self, xlabel):
        """
        Setter of xaxis
        :param xlabel: str
        """
        self._xaxis = LinearAxis(axis_label=xlabel)

    @property
    def yaxis(self):
        """
        :return: yaxis
        """
        return self._yaxis

    @yaxis.setter
    def yaxis(self, ylabel):
        """
        Setter of yaxis.
        If ylabel equals depth or pressure (as defined below): execute self._convert_yaxis_values(ylabel)
        :param ylabel: str
        """
        self._yaxis = LinearAxis(axis_label=ylabel)

        if 'PRES' in ylabel or 'DEP' in ylabel:
            self._convert_yaxis_values(ylabel)


class ProfilePlot(BaseAxes):
    """
    Utilizes interactive plotting tools of Bokeh
    https://bokeh.pydata.org/en/latest/
    """
    def __init__(self, dataframe, parameters=None, tabs=None):
        self.df = dataframe
        self.parameters = parameters
        self.tabs = tabs

        self.TOOLS = "reset,hover,pan,wheel_zoom,box_zoom,lasso_select,save"

        self.TOOLTIPS = [("index", "$index"),
                         ("x-value", "$x"),
                         ("y-value", "$y")]

    def _set_output_file(self, name):
        """
        Sets plot title and creates html output file
        :param name: str, name of profile
        :return: HTML, output file
        """
        self.TITLE = "Profile Plot - " + name
        if name == '':
            name = "profile_plot.html"
        elif not name.endswith('.html'):
            name = name+'.html'

        # online, faster
        output_file(name)

        # offline, slower
        # output_file(name, mode='inline')

    def _convert_yaxis_values(self, ylabel):
        """
        Is activated when y-axis label equals pressure or depth.
        Why? Because we want value 0 (m or dbar) to start on top of the
             plot with an increase downwards instead of upwards.

        Turning all y-axis values negative and than override axis labels,
        hence values are negative while labels are positive

        :param ylabel: str, y label and dataframe key
        """
        self._turn_values_negative(ylabel)
        y_labels = {v: str(abs(v)) for v in range(0, int(min(self.df[ylabel])) * 2, -1)}
        self.yaxis.major_label_overrides = y_labels

    def _turn_values_negative(self, ylabel):
        """
        Is activated when y-axis label equals pressure or depth.
        Turning all y-axis values negative
        :param ylabel: str, y label and dataframe key
        """
        if 'PRES' in ylabel or 'DEP' in ylabel:
            if not any(self.df[ylabel] < 0):
                self.df[ylabel] = -self.df[ylabel]

    def _get_source_selecters(self, x=None, y=None, source=None):
        """
        :param x: str, x-axis parameter
        :param y: str, y-axis parameter
        :param source: bokeh.models.ColumnDataSource
        :return: x- and y-axis selecter
        """
        callback = CustomJS(args={'source': source,
                                  'xaxis': self.xaxis,
                                  'yaxis': self.yaxis}, code="""
                //console.log(' changed selected option', cb_obj.value);

                var data = source.data;

                data['x'] = data[x_param.value];
                data['y'] = data[y_param.value];

                xaxis.attributes.axis_label = x_param.value;
                yaxis.attributes.axis_label = y_param.value;

                xaxis.change.emit();
                yaxis.change.emit();
                source.change.emit();
        """)

        xaxis_selecter = Select(title="x-axis parameter", value=x, options=self.parameters,
                                callback=callback, width=200)
        callback.args["x_param"] = xaxis_selecter

        yaxis_selecter = Select(title="y-axis parameter", value=y, options=self.parameters,
                                callback=callback, width=200)
        callback.args["y_param"] = yaxis_selecter

        return xaxis_selecter, yaxis_selecter

    def _get_xaxis_slider(self, plot_obj):
        """
        Creates an "x-axis slider" that allows the user to interactively change the boundaries of the axes
        :param plot_obj: Bokeh plot object
        :return: x-axis slider
        """
        callback = CustomJS(args={'plot': plot_obj}, code="""
            var a = cb_obj.value;
            plot.x_range.start = a[0];
            plot.x_range.end = a[1];
        """)
        slider = RangeSlider(start=0, end=50, value=(self.df['x'].min(), self.df['x'].max()),
                             step=1, title="x-axis range slider", width=200)
        slider.js_on_change('value', callback)

        return slider

    def _get_data_table(self, source=None):
        """
        Create a data table associated to the plot object
        :param source: bokeh.models.ColumnDataSource
        :return: bokeh.models.widgets.DataTable
        """
        columns = [TableColumn(field="y", title="y-axis data"),
                   TableColumn(field="x", title="x-axis data"),
                   ]
        return DataTable(source=source, columns=columns, width=200)

    def circle_plot(self, x=None, y=None, source=None):
        """
        https://bokeh.pydata.org/en/latest/docs/reference/plotting.html#bokeh.plotting.figure.Figure.circle

        Plot profile using bokeh circle plot

        :param x: str, dataframe key
        :param y: str, dataframe key
        :param source: bokeh.models.sources.ColumnDataSource
        :return: bokeh.plotting.figure.Figure
        """
        plot = figure(# plot_width=800,
                      # x_axis_location="above",
                      # y_axis_location="right",
                      tools=self.TOOLS,
                      tooltips=self.TOOLTIPS,
                      title=self.TITLE)

        plot.background_fill_color = "#dddddd"
        plot.grid.grid_line_color = "white"

        plot.outline_line_width = 1
        plot.outline_line_color = "black"
        plot.axis.visible = False

        plot.circle('x', 'y',
                    source=source,
                    size=12,
                    line_color="lightblue",
                    alpha=0.6)

        # For setting definitions see @xaxis.setter, class BaseAxis
        self.xaxis = x

        # For setting definitions see @yaxis.setter, class BaseAxis
        self.yaxis = y

        plot.add_layout(self.xaxis, 'below')
        plot.add_layout(self.yaxis, 'left')

        return plot

#        p.line(x, y, source=source, color='#A6CEE3')

#        labels = LabelSet(x=x, y=y,
#                          text=z,
#                          y_offset=8,
#                          text_font_size="8pt", text_color="#555555",
#                          source=source, text_align='center')
#        p.add_layout(labels)

    def line_plot(self, x=None, y=None, source=None):
        """
        https://bokeh.pydata.org/en/latest/docs/reference/plotting.html#bokeh.plotting.figure.Figure.line

        Plot profile using bokeh line plot

        :param x: str, dataframe key
        :param y: str, dataframe key
        :param source: bokeh.models.sources.ColumnDataSource
        :return: bokeh.plotting.figure.Figure
        """
        plot = figure(plot_width=800,
                      x_axis_location="above",
                      tools=self.TOOLS,
                      tooltips=self.TOOLTIPS,
                      title=self.TITLE)
        plot.background_fill_color = "#dddddd"
        # plot.xaxis.axis_label = x
        # plot.yaxis.axis_label = y
        plot.grid.grid_line_color = "white"

        plot.line('x', 'y', source=source, color='black')

        # plot.yaxis.major_label_overrides = self.y_labels

        return plot

    def plot(self, x=None, y=None, z=None, name=''):
        """
        :param x: str, dataframe key
        :param y: str, dataframe key
        :param z: str, dataframe key
        :param name: str, name of plot
        :return: Interactive HTML plot
        """
        self._set_output_file(name)

        self._turn_values_negative(y)

        self.df['x'] = self.df[x]
        self.df['y'] = self.df[y]

        source = ColumnDataSource(self.df)

        circle_plot = self.circle_plot(x=x, y=y, source=source)
        line_plot = self.line_plot(x=x, y=y, source=source)

        xrange_slider = self._get_xaxis_slider(circle_plot)

        xaxis_selecter, yaxis_selecter = self._get_source_selecters(x=x, y=y, source=source)

        data_table = self._get_data_table(source=source)

        # show(widgetbox(data_table))

        # spacer = Spacer(width=100, height=100)

        widget_list = [yaxis_selecter, xaxis_selecter, xrange_slider, data_table]

        widgets = WidgetBox(*widget_list)

        col_1 = column(circle_plot, sizing_mode='scale_width')
        col_2 = column(widgets, sizing_mode='scale_width')
        row_1 = row([col_1, col_2], sizing_mode='scale_width')

        # tab1 = Panel(child=row_1, title="circle")#, sizing_mode='scale_width')
        # tab2 = Panel(child=line_plot, title="line")#, sizing_mode='scale_width')
        # tabs = Tabs(tabs=[tab1, tab2])#, sizing_mode='scale_width')
        # #
        # show(tabs)
        show(row_1)

        # row_3 = column(spacer, sizing_mode='scale_both')
        # show(row([col_1, col_2], sizing_mode='scale_width'))
        # show(layout(row([col_1, col_2])))
        # script, div = components((col_1, col_2))
        # show(components([col_1, col_2]))
        # show(row(circle_plot, widgets)) #, sizing_mode='stretch_both'))


class CallBacks(object):
    """

    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def callback_test(source):
        code = """
        // CALLBACK TESTING WITH PRINT
        console.log('console print callback_test!')        
                
        """
        # Create a CustomJS callback
        return CustomJS(args={'source': source},
                        code=code)

    @staticmethod
    def month_selection_callback(position_source=None, position_plot_source=None):
        """
        # TODO We need to rewrite the JScallback code.. not very versatile..
        # simply use all columns from position_source to begin with?

        :param position_source:
        :param position_plot_source:
        :return:
        """
        code = """
        console.log('month_selection_callback');
        // Get data from ColumnDataSource
        var selected_data = {LATIT: [], LONGI: [], STATION: [], KEY: [], MONTH: [], COMNT_VISIT: []};
        var data = source.data;
        
        var month_mapping = {'All': 'All',
                             'January': '01', 'February': '02',
                             'March': '03', 'April': '04',
                             'May': '05', 'June': '06',
                             'July': '07', 'August': '08',
                             'September': '09', 'October': '10',
                             'November': '11', 'December': '12'};

        var selected_month = month_mapping[month.value];

        var key_val, lat_val, lon_val, statn_val, mon_val, cvis_val;
        for (var i = 0; i < data.KEY.length; i++) {
            key_val = data.KEY[i];
            lat_val = data.LATIT[i];
            lon_val = data.LONGI[i];
            statn_val = data.STATION[i];
            mon_val = data.MONTH[i];
            cvis_val = data.COMNT_VISIT[i];

            if (selected_month == 'All') {
                selected_data.KEY.push(key_val);
                selected_data.LATIT.push(lat_val);
                selected_data.LONGI.push(lon_val);
                selected_data.STATION.push(statn_val);
                selected_data.MONTH.push(mon_val);
                selected_data.COMNT_VISIT.push(cvis_val);
            } else if (mon_val == selected_month) {
                selected_data.KEY.push(key_val);
                selected_data.LATIT.push(lat_val);
                selected_data.LONGI.push(lon_val);
                selected_data.STATION.push(statn_val);
                selected_data.MONTH.push(mon_val);
                selected_data.COMNT_VISIT.push(cvis_val);
            }
        }
        
        plot_source.data = selected_data;
        """
        # Create a CustomJS callback with the code and the data
        return CustomJS(args={'source': position_source,
                              'plot_source': position_plot_source},
                        code=code)

    @staticmethod
    def station_callback_2(position_source=None, data_source=None,
                           figures=None, seconds=None, pmap=None,
                           single_select=None):
        # assert position_source, data_source
        code = """
        //console.log('station_callback_2');
        // Set column name to select similar glyphs
        var key = 'KEY';
        var statn_key = 'STATION';
        var sec = seconds.data;

        // Get data from ColumnDataSource
        var position_data = position_source.data;
        var data = data_source.data;
        var parameter_mapping = parameter_mapping;
        var figures = figures;
        var single_select = single_select;
        
        //console.log('parameter_mapping', parameter_mapping);
        
        // Get indices array of all selected items
        var selected = position_source.selected.indices;
        
        //console.log('data[y].length', data['y'].length)
        //console.log('selected', selected);
        
        // Update figure titlesflag_color_mapping 
        var station_name = position_data[statn_key][selected[0]];
        var selected_key = position_data[key][selected[0]];
        
        //console.log('station_name', station_name);
        //console.log('selected_key', selected_key);
        
        // Update active keys in data source    
        if ((single_select == 1 && selected.length == 1) || (single_select == 0)) {
            var data_parameter_name, q0_key, color_key;
            for (var fig_key in figures){
                if ( ! fig_key.startsWith("COMBO")) {
                    data_parameter_name = parameter_mapping[fig_key];
                    q0_key = fig_key+'_q0';
                    color_key = 'color_'+fig_key;
                    
                    data[fig_key] = data[selected_key+'_'+data_parameter_name];
                    data[q0_key] = data[selected_key+'_'+parameter_mapping[q0_key]];
                    data[color_key] = data[selected_key+'_'+color_key];
                }
                figures[fig_key].title.text = station_name + ' - ' + selected_key
            }
            data['y'] = data[selected_key+'_'+parameter_mapping['y']];
    
            // Save changes to ColumnDataSource
            data_source.change.emit();
        }

        var d = new Date();
        var t = d.getTime();
        var new_seconds = Math.round(t / 1000);
        sec.tap_time[0] = new_seconds;
        sec.reset_time[0] = new_seconds;
        seconds.change.emit();
        for (var fig_key in figures){
            figures[fig_key].reset.emit();
        }
        //console.log('station_callback_2 - DONE');
        """
        # Create a CustomJS callback with the code and the data
        return CustomJS(args={'position_source': position_source,
                              'data_source': data_source,
                              'figures': figures,
                              'seconds': seconds,
                              'parameter_mapping': pmap,
                              'single_select': single_select,
                              },
                        code=code)

    @staticmethod
    def lasso_callback(monthly_keys=None, in_data=None, plot_data=None, x_range=None, y_range=None):
        """"""
        code = """
        //console.log('lasso_callback');
        var month_mapping = {'All': 'All',
                             'January': '01', 'February': '02',
                             'March': '03', 'April': '04',
                             'May': '05', 'June': '06',
                             'July': '07', 'August': '08',
                             'September': '09', 'October': '10',
                             'November': '11', 'December': '12'};

        var selected_month = month_mapping[month.value];
        
        var data = {x: [], y: [], color: [], key: []};
        var indices = cb_obj.indices;
        var selected_keys = [];
        for (var i = 0; i < indices.length; i++) {
            selected_keys.push(monthly_keys[selected_month][indices[i]]);
        }
        
        //console.log('selected_keys', selected_keys)
        
        var key_val, x_val, y_val, c_val;
        for (var i = 0; i < in_data.KEY.length; i++) {
            key_val = in_data.KEY[i];
            x_val = in_data.x[i];
            y_val = in_data.y[i];
            c_val = in_data.color[i];

            if (selected_keys.indexOf(key_val) !== -1) {
                data.x.push(x_val);
                data.y.push(y_val);
                data.color.push(c_val);
                data.key.push(key_val);
            }
        }
        if (data.x.length > 1) {
            //console.log('Update!')
            plot_data.data = data;
            x_range.start = Math.min.apply(Math, data.x)-0.5;
            x_range.end = Math.max.apply(Math, data.x)+0.5;            
            y_range.start = Math.min.apply(Math, data.y)-0.5;
            y_range.end = Math.max.apply(Math, data.y)+0.5;
            x_range.change.emit();
            y_range.change.emit();
            //console.log('x_range.start', x_range.start)
        }
        """
        return CustomJS(args=dict(monthly_keys=monthly_keys,
                                  in_data=in_data.data,
                                  plot_data=plot_data,
                                  x_range=x_range,
                                  y_range=y_range),
                        code=code)

    @staticmethod
    def comnt_callback(position_source=None, comnt_obj=None, single_select=None):
        # assert position_source, data_source
        code = """
        //console.log('comnt_callback');
        // Set column name to select similar glyphs
        var key = 'KEY';
        var statn_key = 'STATION';
        var comnt_key = 'COMNT_VISIT';

        // Set Sources
        var position_data = position_source.data;
        var comnt_obj = comnt_obj;
        var single_select = single_select;

        // Get indices array of all selected items
        var selected = position_source.selected.indices;

        // Update figure title
        var station_name = position_data[statn_key][selected[0]];
        var selected_key = position_data[key][selected[0]];
        var comnt = position_data[comnt_key][selected[0]];

        // Update active keys in data source    
        if ((single_select == 1 && selected.length == 1) || (single_select == 0)) {
            comnt_obj.value = comnt
            comnt_obj.title = comnt_key + ':  ' + station_name + ' - ' + selected_key
        }

        """
        # Create a CustomJS callback with the code and the data
        return CustomJS(args={'position_source': position_source,
                              'comnt_obj': comnt_obj,
                              'single_select': single_select,
                              },
                        code=code)

    @staticmethod
    def change_button_type_callback(button=None, btype=None):
        """"""
        code = """
        button.button_type = btype;
        """
        return CustomJS(args={'button': button, 'btype': btype}, code=code)

    def select_button(self, data_source=None):
        """"""
        code = """
        var data = data_source.data;
        var indices = [];
        
        var i = 0;
        while ( ! isNaN(data.y[i]) ) {
            indices.push(i)
            i++
        }
        data_source.selected.indices = indices;
        button.button_type = 'success';
        //console.log('select_button DONE');
        """
        button = Button(label="Select all", width=30, button_type="default")
        callback = CustomJS(args={'data_source': data_source, 'button': button}, code=code)
        button_type_callback = self.change_button_type_callback(button=button, btype='success')
        button.js_on_event(ButtonClick, callback, button_type_callback)
        return button

    @staticmethod
    def deselect_button(data_source=None):
        """"""
        code = """
        data_source.selected.indices = [];
        """
        callback = CustomJS(args={'data_source': data_source}, code=code)
        button = Button(label="Deselect all", width=30, button_type="default")
        button.js_on_event(ButtonClick, callback)
        return button

    @staticmethod
    def range_slider_update_callback(slider=None, data_source=None):
        """"""
        code = """
        var data = data_source.data;        
        var values = [];
        var i = 0;
        while ( ! isNaN(data.y[i]) ) {
            values.push(data.y[i])
            i++
        }
        slider.start = Math.min.apply(Math, values);
        slider.end = Math.max.apply(Math, values);
        slider.value = [slider.start, slider.end];
        slider.change.emit();
        """
        return CustomJS(args={'slider': slider, 'data_source': data_source},
                        code=code)

    @staticmethod
    def range_selection_callback(data_source=None):
        """"""
        code = """
        var data = data_source.data;
        var min_pres = cb_obj.value[0];
        var max_pres = cb_obj.value[1];
        var indices = [];
        for (var i = 0; i < data.y.length; i++) {
            if ((data.y[i] >= min_pres) && (data.y[i] <= max_pres)) {
                indices.push(i)
            }
        }
        data_source.selected.indices = indices;
        """
        return CustomJS(args={'data_source': data_source},
                        code=code)

    @staticmethod
    def get_flag_widget(position_source, data_source, flag_key=None, color_key=None):
        """"""
        code = """
        console.log('get_flag_widget');
        var flag_color_mapping = {'A-flag': {'c':'navy', 'flag': ''},
                                  'B-flag': {'c':'red', 'flag': 'B'},
                                  'E-flag': {'c':'green', 'flag': 'E'},
                                  'S-flag': {'c':'orange', 'flag': 'S'}};

        // Get data from ColumnDataSource
        var position_data = position_source.data;
        var data = data_source.data;

        // Set variables attributes
        var color_column = color_key;
        var selected_flag = flag_selection.value;

        var selected_position = position_source.selected.indices;
        var selected_key = position_data['KEY'][selected_position[0]];
        var flag_column = selected_key+'_'+flag_key;

        // Get indices array of all selected items
        var selected_indices = data_source.selected.indices;

        for (var i = 0; i < selected_indices.length; i++) {
            data[color_column][selected_indices[i]] = flag_color_mapping[selected_flag]['c'];
            data[flag_column][selected_indices[i]] = flag_color_mapping[selected_flag]['flag'];
            // console.log('data[flag_column][selected_indices[i]]', data[flag_column][selected_indices[i]])
        }

        // Save changes to ColumnDataSource
        data_source.change.emit();
        """
        callback = CustomJS(args={'position_source': position_source,
                                  'data_source': data_source},
                            code=code)
        flag_selector = Select(value='A-flag',
                               options=['A-flag', 'B-flag', 'E-flag', 'S-flag'],
                               width=100)
        callback.args["flag_selection"] = flag_selector
        callback.args["color_key"] = color_key
        callback.args["flag_key"] = flag_key
        button = Button(label="Flag Data", width=50)
        button.js_on_event(ButtonClick, callback)

        return row([flag_selector, button], sizing_mode="stretch_width")

    @staticmethod
    def get_flag_buttons_widget(position_source, data_source, datasets, flag_key=None,
                                color_key=None, figure_objs=None, select_button=None):
        """"""
        code = """
        //console.log('get_flag_buttons_widget');
        var flag_color_mapping = {'A-flag': {'c':'navy', 'flag': ''},
                                  'B-flag': {'c':'red', 'flag': 'B'},
                                  'E-flag': {'c':'green', 'flag': 'E'},
                                  'S-flag': {'c':'orange', 'flag': 'S'}};

        // Get data from ColumnDataSource
        var position_data = position_source.data;
        var data = data_source.data;
        var select_button_type = select_button.button_type;

        // Set variables attributes
        var color_column = color_key;
        var selected_flag = flag;

        var selected_position = position_source.selected.indices;
        var selected_key = position_data['KEY'][selected_position[0]];
        var flag_column = selected_key+'_'+flag_key;

        // Get indices array of all selected items
        var selected_indices = data_source.selected.indices;

        var patches = {
            color_column : [],
            flag_column : [],
        };
        
        var flag_value = flag_color_mapping[selected_flag]['flag'];
        var color_value = flag_color_mapping[selected_flag]['c'];
        var color_tuple, flag_tuple, index_value;
        
        //console.log('flag_value', flag_value)
        //console.log('color_value', color_value)
        //console.log('patches', patches)
        //console.log('selected_indices.length', selected_indices.length)
        
        if (selected_position.length == 1) {
            for (var i = 0; i < selected_indices.length; i++) {
                index_value = selected_indices[i];
                color_tuple = (index_value, color_value);
                flag_tuple = (index_value, flag_value);
                
                //console.log('index_value', index_value)
                //console.log('color_tuple', color_tuple)
                //console.log('flag_tuple', flag_tuple)
                
                data[color_column][index_value] = color_value;
                data[flag_column][index_value] = flag_value;
            }
    
            // Save changes to ColumnDataSource (only on the plotting side of ColumnDataSource)
            data_source.change.emit();
            for (var key in figure_objs) {
                figure_objs[key].reset.emit();
            }
            data_source.selected.indices = selected_indices;
            select_button.button_type = select_button_type;
            
            // Trigger python callback inorder to save changes to the actual datasets
            dummy_trigger.glyph.size = Math.random();
            dummy_trigger.glyph.change.emit();
            
        } else {
            console.log('To many selected stations!! We can only work with one at a time', selected_position.length)
        }
        """
        flag_color_mapping = {'A-flag': {'c': 'navy', 'flag': ''},
                              'B-flag': {'c': 'red', 'flag': 'B'},
                              'E-flag': {'c': 'green', 'flag': 'E'},
                              'S-flag': {'c': 'orange', 'flag': 'S'}}

        def callback_py(attr, old, new, flag=None):
            start_time = time.time()
            selected_position = position_source.selected.indices
            if len(selected_position) > 1:
                print('multi serie selection, no good! len(selected_position) = {}'.format(len(selected_position)))
                return

            selected_key = position_source.data['KEY'][selected_position[0]]
            selected_indices = data_source.selected.indices
            # ds_key = self.key_ds_mapper.get(selected_key)
            ds_key = ''.join(('ctd_profile_', selected_key, '.txt'))
            flag_value = flag_color_mapping[flag].get('flag')
            datasets[ds_key]['data'][flag_key].iloc[selected_indices] = flag_value
            print('datasets update in -- %.3f sec' % (time.time() - start_time))

        # button_types = default, primary, success, warning or danger
        button_types = ['primary', 'danger', 'success', 'warning']
        flag_list = ['A-flag', 'B-flag', 'E-flag', 'S-flag']
        button_list = [Spacer(width=10)]
        dummy_figure = figure()
        for flag, b_type in zip(flag_list, button_types):

            dummy_trigger = dummy_figure.circle(x=[1], y=[2], alpha=0)
            dummy_trigger.glyph.on_change('size', partial(callback_py, flag=flag))

            callback = CustomJS(args={'position_source': position_source,
                                      'data_source': data_source,
                                      'figure_objs': figure_objs,
                                      'flag': flag,
                                      'dummy_trigger': dummy_trigger,
                                      'select_button': select_button},
                                code=code)

            callback.args["color_key"] = color_key
            callback.args["flag_key"] = flag_key

            button = Button(label=flag, width=30, button_type=b_type)
            button.js_on_event(ButtonClick, callback)

            button_list.append(button)

        button_list.append(Spacer(width=10))

        return row(button_list, sizing_mode="stretch_width")

    def get_download_widget(self, datasets, series, session):
        """"""
        def callback_download(event):
            def serie_generator(datasets_filelist, selected_keylist):
                for name in datasets_filelist:
                    for key in selected_keylist:
                        if key in name:
                            yield name, key

            def append_qc_comment(meta):
                time_stamp = get_time_as_format(now=True, fmt='%Y%m%d%H%M')
                meta[len(meta) + 1] = '//COMNT_QC; MANUAL QC PERFORMED BY {}; TIMESTAMP {}'.format(
                    session.settings.user, time_stamp)

            # def update_flags(df, key):
            #     idx = np.where(np.isfinite(self.data_source.data[key+'_PRES_CTD [dbar]']))[0]
            #     for qf in df.columns:
            #         if qf.startswith('Q_'):
            #             if key+'_'+qf in self.data_source.data:
            #                 df[qf] = self.data_source.data[key+'_'+qf][idx]

            if not any(series.selected.indices):
                print('No selected series to download')
                print('len(series.selected.indices)', series.selected.indices)
                return

            start_time = time.time()
            generator = serie_generator(datasets.keys(),
                                        [series.data['KEY'][idx] for idx in series.selected.indices])

            datasets_to_update = {}
            for ds_name, serie_key in generator:
                append_qc_comment(datasets[ds_name]['metadata'])
                # update_flags(datasets[ds_name]['data'], serie_key)
                datasets_to_update[ds_name] = datasets[ds_name]

            if any(datasets_to_update):
                session.save_data([datasets_to_update], writer='ctd_standard_template')
                print('Download completed! -- %.3f sec' % (time.time() - start_time))
            else:
                print('No download!')

        button = Button(label="Download selected data", button_type="success", width=40)
        button.on_event(ButtonClick, callback_download)
        return button

    @staticmethod
    def comnt_visit_change_button(datasets=None, position_source=None, comnt_obj=None):
        """"""
        def callback_py(attr, old, new, comnt_obj=None):
            selected_indices = position_source.selected.indices
            if len(selected_indices) > 1:
                print('multi serie selection, no good! len(selected_position) = {}'.format(len(selected_indices)))
                return
            selected_key = position_source.data['KEY'][selected_indices[0]]
            ds_key = ''.join(('ctd_profile_', selected_key, '.txt'))
            cv_boolean = datasets[ds_key]['metadata'].str.startswith('//METADATA;COMNT_VISIT;')
            datasets[ds_key]['metadata'][cv_boolean] = '//METADATA;COMNT_VISIT;' + comnt_obj.value

        js_code = """
        console.log('comnt_visit_change_button')
        // Get data from ColumnDataSource
        var comnt_column = 'COMNT_VISIT';
        var position_data = position_source.data;

        // Set variables attributes
        var new_comnt = comnt_obj.value;
        var selected_indices = position_source.selected.indices;
        
        if (selected_indices.length == 1) {
            position_data[comnt_column][selected_indices[0]] = new_comnt;
            
            // Save changes to ColumnDataSource
            position_source.change.emit();
            
            // Trigger python callback inorder to save changes to the actual datasets
            dummy_trigger.glyph.size = Math.random();
            dummy_trigger.glyph.change.emit();
            
        } else {
            console.log('To many selected stations!! We can only work with one at a time', selected_indices.length)
        }
        """
        dummy_figure = figure()
        dummy_trigger = dummy_figure.circle(x=[1], y=[2], alpha=0)
        dummy_trigger.glyph.on_change('size', partial(callback_py, comnt_obj=comnt_obj))

        callback = CustomJS(args={'position_source': position_source,
                                  'comnt_obj': comnt_obj,
                                  'dummy_trigger': dummy_trigger},
                            code=js_code)

        button = Button(label="Commit", width=30, button_type="success")
        button.js_on_event(ButtonClick, callback)
        return button

    @staticmethod
    def get_file_widget():
        # button_input = FileInput(accept=".csv,.txt")
        button_input = FileInput()

        return button_input

    @staticmethod
    def add_hlinked_crosshairs(*figs):
        js_move = """
        for (var cross_key in other_crosses){
            other_crosses[cross_key].spans.width.computed_location = cb_obj.sy;
        }
        current_cross.spans.height.computed_location = null;
        """
        js_leave = """
        for (var cross_key in other_crosses){
            other_crosses[cross_key].spans.width.computed_location = null;
        }
        """
        cross_objs = {}
        fig_objs = {}
        for i, f in enumerate(figs):
            cross_objs[i] = CrosshairTool(line_alpha=0.5)
            fig_objs[i] = f
            fig_objs[i].add_tools(cross_objs[i])

        for i in range(len(cross_objs)):
            other_crosses = {ii: cross_objs[ii] for ii in range(len(cross_objs)) if ii != i}
            if i != len(cross_objs)-1:
                args = {'current_cross': cross_objs[i], 'other_crosses': other_crosses, 'fig': fig_objs[i+1]}
            else:
                args = {'current_cross': cross_objs[i], 'other_crosses': other_crosses, 'fig': fig_objs[0]}

            fig_objs[i].js_on_event('mousemove', CustomJS(args=args, code=js_move))
            fig_objs[i].js_on_event('mouseleave', CustomJS(args=args, code=js_leave))

    # @staticmethod
    # def render_callback(source=None, x_range_dict=None):
    #     """"""
    #     return CustomJS(args={'source': source, 'xr': x_range_dict}, code="""
    #             var geometry = cb_data['geometry'];
    #             var y_data = geometry.y; // current mouse y position in plot coordinates
    #             //console.log("(,y)=", y_data)
    #             var data = {'tempx': [xr.xr_temp.start, xr.xr_temp.end],
    #                         'saltx': [xr.xr_salt.start, xr.xr_salt.end],
    #                         'doxyx': [xr.xr_doxy.start, xr.xr_doxy.end],
    #                         'y': [y_data, y_data]};
    #             source.data = data;
    #             cb_obj.reset.emit();
    #         """)

    @staticmethod
    def x_range_callback(x_range_obj=None, delta=4, seconds=None):
        code = """
        //console.log('x_range_callback');
        var sec = seconds.data;
        var d = new Date();
        var t = d.getTime();
        var new_seconds = t / 1000;
        var tap_time_delta = new_seconds - sec.tap_time[0];
        var reset_time_delta = new_seconds - sec.reset_time[0];
        var delta_add;
        if (tap_time_delta < 1.5 || reset_time_delta < 1.5) {
            var start = xr.start;
            var end = xr.end;
            var x_delta = end - start;
            if (x_delta < accepted_delta) {
                delta_add = (accepted_delta - x_delta) / 2;
                end = end + delta_add;
                start = start - delta_add;
            }
            xr.end = end;
            xr.start = start;
        }
        """
        return CustomJS(args={'xr': x_range_obj,
                              'seconds': seconds,
                              'accepted_delta': delta},
                        code=code)

    @staticmethod
    def reset_callback(seconds):
        code = """
        //console.log('reset_callback');
        var sec = seconds.data;
        var d = new Date();
        var t = d.getTime();
        sec.reset_time[0] = t / 1000;
        //console.log('sec.reset_time[0]', sec.reset_time[0])
        seconds.change.emit();
        """
        return CustomJS(args={'seconds': seconds},
                        code=code)

    @staticmethod
    def reset_all_callback(figures):
        code = """
        console.log('reset_all_callback');
        for (var i = 0; i < figure_objs.length; i++) {
            figure_objs[i].reset.emit();
        }
        """
        return CustomJS(args={'figure_objs': figures},
                        code=code)


class QCWorkTool(CallBacks):
    """
    """
    def __init__(self, dataframe, datasets=None, parameters=None, color_fields=None, qflag_fields=None, auto_q_flag_parameters=None,
                 tabs=None, plot_parameters_mapping=None, ctdpy_session=None, multi_sensors=False, combo_plots=False, output_filename="CTD_QC_VIZ.html", output_as_notebook=False):
        super().__init__()
        self.seconds = ColumnDataSource(data=dict(tap_time=[None], reset_time=[None]))
        self.ctd_session = ctdpy_session
        self.multi_sensors = multi_sensors
        self.combo_plots = combo_plots

        self.map = None
        # self.selected_series = None
        # self.df = dataframe
        self.datasets = datasets
        self.key_ds_mapper = self.get_mapper_key_to_ds()
        self.parameters = parameters
        self.plot_parameters_mapping = plot_parameters_mapping
        self.color_fields = color_fields
        self.qflag_fields = qflag_fields
        self.auto_qflag_fields = auto_q_flag_parameters
        self.tabs = tabs
        self.output_as_notebook = output_as_notebook
        if self.output_as_notebook:
            output_notebook()
        else:
            output_file(output_filename)

        self.tile_provider = get_provider(Vendors.CARTODBPOSITRON_RETINA)

        self.figures = {}
        xrange_callbacks = {}
        y_range_setting = None
        for p in self.plot_parameters_mapping:
            if p == 'y' or 'q' in p:
                continue
            param = self.plot_parameters_mapping.get(p)
            self.figures[p] = figure(tools="pan,reset,wheel_zoom,lasso_select,save", active_drag="lasso_select",
                                     title="", height=400, width=400,
                                     y_range=y_range_setting,
                                     tooltips=[(param, "@{}".format(p)),
                                               ("Pressure [dbar]", "@y"),
                                               ("Auto-QC", "@{}_q0".format(p))])
            self.figures[p].title.align = 'center'
            self.figures[p].xaxis.axis_label = param
            self.figures[p].xaxis.axis_label_text_font_style = 'bold'
            self.figures[p].ygrid.band_fill_alpha = 0.05
            self.figures[p].ygrid.band_fill_color = "black"
            self.figures[p].toolbar.active_scroll = self.figures[p].select_one(WheelZoomTool)

            if not y_range_setting or (self.multi_sensors and p == 'x4'):
                self.figures[p].yaxis.axis_label = 'Pressure (dbar)'
                self.figures[p].yaxis.axis_label_text_font_style = 'bold'

            y_range_setting = y_range_setting or self.figures[p].y_range

            xrange_callbacks[p] = self.x_range_callback(x_range_obj=self.figures[p].x_range, seconds=self.seconds)
            self.figures[p].x_range.js_on_change('start', xrange_callbacks[p])

        if self.combo_plots and self.multi_sensors:
            for name, p1, p2 in zip(('COMBO_TEMP', 'COMBO_SALT', 'COMBO_DOXY'),
                                    ('x1', 'x2', 'x3'),
                                    ('x4', 'x5', 'x6')):
                param = self.plot_parameters_mapping.get(p1)
                self.figures[name] = figure(tools="pan,reset,wheel_zoom,lasso_select,save", active_drag="lasso_select",
                                             title="", height=400, width=400,
                                             y_range=y_range_setting,
                                            )
                self.figures[name].title.align = 'center'
                self.figures[name].xaxis.axis_label = param
                self.figures[name].xaxis.axis_label_text_font_style = 'bold'
                self.figures[name].ygrid.band_fill_alpha = 0.05
                self.figures[name].ygrid.band_fill_color = "black"
                self.figures[name].toolbar.active_scroll = self.figures[name].select_one(WheelZoomTool)

                if p1 == 'x1':
                    self.figures[name].yaxis.axis_label = 'Pressure (dbar)'
                    self.figures[name].yaxis.axis_label_text_font_style = 'bold'

        self.add_hlinked_crosshairs(*(fig_obj for i, fig_obj in self.figures.items()))

        self.ts = figure(title="CTD TS Diagram", tools=[PanTool(), WheelZoomTool(), ResetTool(), SaveTool()],
                         tooltips=[("Serie", "@key")], height=400, width=400,
                         x_range=(2, 36), y_range=(-2, 20))
        self.ts.title.align = 'center'

        self._setup_position_source(dataframe)
        self._setup_data_source(dataframe)
        self._setup_TS_source(dataframe)
        self._setup_month_selector()
        self._setup_comnt_inputs()
        self._setup_selection_widgets()
        self._setup_flag_widgets()
        self._setup_reset_callback(**xrange_callbacks)
        self._setup_datasource_callbacks()
        self._setup_download_button()
        self._setup_get_file_button()
        self._setup_serie_table()
        self._setup_info_block()
        self._setup_map()

        self.ts_axis_ranges = {'t_min': 0, 't_max': 25, 's_min': 2, 's_max': 36}

    def get_mapper_key_to_ds(self):
        #TODO would we like to create this mapper in any other way?
        # Let´s say that the dataset name doesnt starts with "ctd_profile_"
        # mapper = {}
        # for key, item in self.datasets.items():
        #
        return {ds_name.strip('ctd_profile_|.txt'): ds_name for ds_name in self.datasets}

    @staticmethod
    def _get_monthly_keys(position_df):
        """"""
        # FIXME Is this really necessary ?
        dictionary = {'All': position_df['KEY'].to_list()}
        for month in [str(m).zfill(2) for m in range(1, 13)]:
            boolean = position_df['MONTH'] == month
            dictionary[month] = position_df.loc[boolean, 'KEY'].to_list()
        return dictionary

    def _setup_position_source(self, df):
        """
        :return:
        """
        position_df = df[['STATION', 'LATITUDE_DD', 'LONGITUDE_DD', 'KEY', 'MONTH']].drop_duplicates(
            keep='first').reset_index(drop=True)
        # boolean = position_df['LATITUDE_DD'].isna()
        xs, ys = convert_projection(position_df['LATITUDE_DD'].astype(float).values, position_df['LONGITUDE_DD'].astype(float).values)
        position_df['LONGI'] = xs
        position_df['LATIT'] = ys

        comnts = []
        for key in position_df['KEY']:
            ds_meta = self.datasets[self.key_ds_mapper.get(key)]['metadata']
            cv_boolean = ds_meta.str.startswith('//METADATA;COMNT_VISIT;')
            value = ds_meta[cv_boolean].values[0].replace('//METADATA;COMNT_VISIT;', '')
            comnts.append(value)
        position_df['COMNT_VISIT'] = comnts

        self.monthly_keys = self._get_monthly_keys(position_df)
        self.position_source = ColumnDataSource(data=position_df)
        self.position_plot_source = ColumnDataSource(data=position_df)

    def _setup_month_selector(self):
        """"""
        callback = self.month_selection_callback(position_source=self.position_source,
                                                 position_plot_source=self.position_plot_source)
        self.month_selector = Select(title="Select month",
                                     value='All',
                                     options=['All'] + pd.date_range(start='2020-01', freq='M', periods=12).month_name().to_list(),
                                     # callback=callback,
                                     # width=120,
                                     )
        self.month_selector.js_on_change('value', callback)
        # self.month_selector.title.text_align = 'center'
        callback.args["month"] = self.month_selector

    def _setup_download_button(self):
        """"""
        self.download_button = self.get_download_widget(self.datasets,
                                                        self.position_plot_source,
                                                        self.ctd_session)

    def _setup_get_file_button(self):
        """"""
        self.file_button = self.get_file_widget()

    def _setup_serie_table(self):
        """
        Create a data table associated to the plot object
        :param source: bokeh.models.ColumnDataSource
        :return: bokeh.models.widgets.DataTable
        """
        columns = [TableColumn(field="STATION", title="Station"),
                   TableColumn(field="KEY", title="Key"),
                   ]
        self.selected_series = DataTable(source=self.position_plot_source, columns=columns,
                                         width=300, height=322)

    def _setup_flag_widgets(self):
        """
        Options:
        self.get_flag_widget(*args, **kwargs)
        self.get_flag_buttons_widget(*args, **kwargs)
        """
        self.flag_widgets = {}
        for fig_key in self.figures.keys():
            if fig_key.startswith('COMBO'):
                continue
            q_key = 'Q_' + self.plot_parameters_mapping.get(fig_key).split()[0]
            self.flag_widgets[fig_key] = self.get_flag_buttons_widget(self.position_plot_source,
                                                                      self.data_source,
                                                                      self.datasets,
                                                                      figure_objs=self.figures,
                                                                      flag_key=q_key,
                                                                      color_key='color_{}'.format(fig_key),
                                                                      select_button=self.select_all_button)

    def _setup_TS_source(self, df):
        """
        :return:
        """
        params = self.parameters + ['KEY']
        ts_df = df[params]
        ts_df.loc[:, 'x'] = ts_df[self.plot_parameters_mapping.get('x2')]  # x2 = SALT
        ts_df.loc[:, 'y'] = ts_df[self.plot_parameters_mapping.get('x1')]  # x1 = TEMP
        ts_df.loc[:, 'color'] = get_color_palette(dep_serie=ts_df[self.plot_parameters_mapping.get('y')])
        self.ts_source = ColumnDataSource(data=ts_df)
        self.ts_plot_source = ColumnDataSource(data=dict(x=[], y=[], color=[], key=[]))

    def _setup_data_source(self, df):
        """
        :return:
        """
        print('Setting up data source structure...')
        # self.df[self.parameters] = self.df[self.parameters].astype(float)
        data_dict = {}
        for key in self.position_source.data['KEY']:
            data_boolean = df['KEY'] == key
            for parameter in self.parameters + self.color_fields + self.qflag_fields + self.auto_qflag_fields:
                data_key = '_'.join((key, parameter))
                data_dict[data_key] = df.loc[data_boolean, parameter].values

        length = 0
        for key in data_dict:
            l = len(data_dict[key])
            if l > length:
                length = l
        for key in data_dict:
            if len(data_dict[key]) < length:
                data_dict[key] = np.pad(data_dict[key],
                                        (0, length-len(data_dict[key])),
                                        'constant',
                                        constant_values=np.nan)

        for p in self.plot_parameters_mapping.keys():
            data_dict[p] = [1] * length
            if p != 'y':
                data_dict['color_'+p] = ['black'] * length

        self.data_source = ColumnDataSource(data=data_dict)

        print('\nData source structure completed!\n')

    def _setup_comnt_inputs(self):
        """
        :return:
        """
        self.comnt_samp = TextInput(value="", title="COMNT_SAMP:")
        self.comnt_visit = TextInput(value="", title="COMNT_VISIT:")
        self.comnt_visit_button = self.comnt_visit_change_button(datasets=self.datasets,
                                                                 position_source=self.position_plot_source,
                                                                 comnt_obj=self.comnt_visit)

    def _setup_info_block(self):
        """
        :return:
        """
        text = """
        <h4>Info links</h4>
        <ul>
          <li><a href="https://docs.bokeh.org/en/latest/docs/user_guide/tools.html" target="_blank">Bokeh toolbar info</a></li>
          <li><a href="https://github.com/sharksmhi/sharkpylib/tree/master/sharkpylib/qc" target="_blank">SHARK-QC-library</a></li>
        </ul>
        
        <h4>QC routines</h4>
        <ol>
          <li>Range check</li>
          <li>Increase check</li>
          <li>Decrease check</li>
          <li>Sensor diff check</li>
          <li>Spike check</li>
        </ol>
        """
        self.info_block = Div(text=text, width=200, height=100)

    def _setup_selection_widgets(self):
        """
        :return:
        """
        self.select_all_button = self.select_button(data_source=self.data_source)
        self.deselect_all_button = self.deselect_button(data_source=self.data_source)

        self.pressure_slider = RangeSlider(start=0, end=100, value=(0, 100),
                                           step=0.5, title="Select with pressure range", width=300)
        callback = self.range_selection_callback(data_source=self.data_source)
        self.pressure_slider.js_on_change('value', callback)

    def _setup_reset_callback(self, **kwargs):
        """"""
        # Autoreset all figures on xrange
        for p, item in self.figures.items():
            xr_cbs = (xr_cb for i, xr_cb in kwargs.items())
            self.figures[p].js_on_event('reset', self.reset_callback(self.seconds),
                                        *xr_cbs)

    def _setup_datasource_callbacks(self):
        """"""
        set_button_type_callback = self.change_button_type_callback(button=self.select_all_button,
                                                                    btype='default')
        self.data_source.selected.js_on_change('indices', set_button_type_callback)

    def _setup_map(self):
        """"""

        pan = PanTool()
        save = SaveTool()
        tap = TapTool()
        lasso = LassoSelectTool()
        reset = ResetTool()
        wheel = WheelZoomTool()

        tooltips = HoverTool(tooltips=[("Station", "@STATION"),
                                       ("Serie", "@KEY")])

        # range bounds supplied in web mercator coordinates
        self.map = figure(x_range=(0, 4000000), y_range=(7100000, 9850000),
                          x_axis_type="mercator", y_axis_type="mercator",  plot_height=420, plot_width=1000, #  width=1210,
                          tools=[pan, wheel, tap, lasso, tooltips, reset, save])

        self.map.yaxis.axis_label = ' '  # in order to aline y-axis with figure window below
        self.map.toolbar.active_scroll = self.map.select_one(WheelZoomTool)
        self.map.add_tile(self.tile_provider)

        # tap.callback = self.station_callback(position_source=self.position_plot_source,
        #                                      data_source=self.data_source,
        #                                      temp_obj=self.temp,
        #                                      salt_obj=self.salt,
        #                                      doxy_obj=self.doxy,
        #                                      seconds=self.seconds)
        station_data_callback = self.station_callback_2(position_source=self.position_plot_source,
                                                        data_source=self.data_source,
                                                        figures=self.figures,
                                                        seconds=self.seconds,
                                                        pmap=self.plot_parameters_mapping,
                                                        single_select=0)
        tap.callback = station_data_callback

        # When we mark stations on the map using lasso selection, we activate the TS-diagram.
        lasso_callback = self.lasso_callback(monthly_keys=self.monthly_keys,
                                             in_data=self.ts_source,
                                             plot_data=self.ts_plot_source,
                                             x_range=self.ts.x_range,
                                             y_range=self.ts.y_range)

        station_data_callback_2 = self.station_callback_2(position_source=self.position_plot_source,
                                                          data_source=self.data_source,
                                                          figures=self.figures,
                                                          seconds=self.seconds,
                                                          pmap=self.plot_parameters_mapping,
                                                          single_select=1)

        comnt_callback = self.comnt_callback(position_source=self.position_plot_source,
                                             comnt_obj=self.comnt_visit,
                                             single_select=1)

        update_slider_callback = self.range_slider_update_callback(slider=self.pressure_slider,
                                                                   data_source=self.data_source)

        select_button_type_callback = self.change_button_type_callback(button=self.select_all_button, btype='default')

        lasso_callback.args["month"] = self.month_selector
        self.position_plot_source.selected.js_on_change('indices',
                                                        lasso_callback,
                                                        station_data_callback_2,
                                                        comnt_callback,
                                                        update_slider_callback,
                                                        select_button_type_callback)

    def plot_stations(self):
        """"""
        renderer = self.map.circle('LONGI', 'LATIT', source=self.position_plot_source,
                                   color="#5BC798", line_color="aquamarine", size=10, alpha=0.7)

        selected_circle = Circle(fill_alpha=0.5, fill_color="#FF0202", line_color="aquamarine")
        nonselected_circle = Circle(fill_alpha=0.3, fill_color="#5BC798", line_color="aquamarine")

        renderer.selection_glyph = selected_circle
        renderer.nonselection_glyph = nonselected_circle

    def plot_data(self):
        """
        self.temp.circle('x1b', 'y', color="deepskyblue", size=8, alpha=0.5, source=self.data_source, legend='Sensor 2')
        self.temp.legend.location = "top_left"
        :return:
        """
        combo_mapping = {'COMBO_TEMP': ('x1', 'x4'), 'COMBO_SALT': ('x2', 'x5'), 'COMBO_DOXY': ('x3', 'x6')}
        legend_mapper = {'x1': 'TEMP 1', 'x2': 'SALT 1', 'x3': 'DOXY 1',
                         'x4': 'TEMP 2', 'x5': 'SALT 2', 'x6': 'DOXY 2'}

        nonselected_circle = Circle(fill_alpha=0.1, fill_color="#898989", line_color="lightgrey")

        for p, item in self.figures.items():
            if p.startswith('COMBO'):
                p1, p2 = combo_mapping.get(p)
                item.line(p1, 'y', color="color_{}".format(p1), line_color="navy", line_width=1, alpha=0.3, source=self.data_source)
                item.circle(p1, 'y', color="color_{}".format(p1), line_color="white", size=6, alpha=0.5, source=self.data_source)

                item.line(p2, 'y', color="color_{}".format(p2), line_color="navy", line_width=1, alpha=0.3, source=self.data_source)
                item.cross(p2, 'y', color="color_{}".format(p2), size=6, alpha=0.5, source=self.data_source)

                item.y_range.flipped = True
                # item.legend.location = "top_right"
            else:
                item.line(p, 'y', color="color_{}".format(p), line_color="navy", line_width=1, alpha=0.3, source=self.data_source) #, legend_label=p)
                renderer = item.circle(p, 'y', color="color_{}".format(p), line_color="white", size=6, alpha=0.5, source=self.data_source) #, legend_label=p)
                renderer.nonselection_glyph = nonselected_circle
                item.y_range.flipped = True

        # T/S - diagram
        self.ts.circle('x', 'y', color='color', size=3, alpha=0.8, source=self.ts_plot_source, legend_label='Sensor 1')
        self.ts.toolbar.active_scroll = self.ts.select_one(WheelZoomTool)
        self.ts.legend.location = "top_left"

        number_of_colors = int(self.ts_source.data[self.plot_parameters_mapping.get('y')].max()) * 2 + 1
        cm_map = cm.get_cmap('cool', number_of_colors)
        color_array = [colors.to_hex(cm_map(c)) for c in range(number_of_colors)]

        color_bar = ColorBar(color_mapper=LinearColorMapper(palette=color_array, low=0, high=self.ts_source.data[self.plot_parameters_mapping.get('y')].max()),
                             # border_line_color='black',
                             location=(0, 0),
                             )

        self.ts.add_layout(color_bar, 'right')

        x_min, x_max, y_min, y_max = 0, 40, -10, 30
        contour_data = get_contour_data(x_min, x_max, y_min, y_max)
        for key in contour_data.keys():
            self.ts.line(contour_data[key]['salt'], contour_data[key]['temp'],
                         line_color="grey", line_alpha=0.8, line_width=1.5)

    def append_qc_comment(self, meta_series):
        """
        :param metadata:
        :return:
        """
        time_stamp = get_time_as_format(now=True, fmt='%Y%m%d%H%M')
        meta_series[len(meta_series) + 1] = '//QC_COMNT; MANUAL QC PERFORMED BY {}; TIMESTAMP {}'.format(
            self.ctd_session.settings.user, time_stamp)

    def get_tab_layout(self):
        fig_tabs = [Panel(child=column([Spacer(height=30), self.ts]), title="TS")]
        for p, item in self.figures.items():
            if (self.multi_sensors and p not in ['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'COMBO_TEMP', 'COMBO_SALT', 'COMBO_DOXY']) \
                    or (not self.multi_sensors and p not in ['x1', 'x2', 'x3']):
                tab_layout = column([self.flag_widgets[p], item])
                tab_name = self.plot_parameters_mapping.get(p).split()[0].replace('_CTD', '')
                pan = Panel(child=tab_layout, title=tab_name)
                fig_tabs.append(pan)

        return Tabs(tabs=fig_tabs)

    def get_tabs(self, **kwargs):
        """
        :param kwargs:
        :return:
        """
        tabs = []
        for name, item in kwargs.items():
            tab = column([self.__getattribute__(attr) for attr in item])
            pan = Panel(child=tab, title=name)
            tabs.append(pan)

        return Tabs(tabs=tabs)

    def get_std_parameter_tab_layout(self):
        def pan_title(string):
            return string.split()[0].replace('_CTD', '')

        columns = []

        if self.multi_sensors:
            for params in zip(('x1', 'x2', 'x3'), ('x4', 'x5', 'x6'), ('COMBO_TEMP', 'COMBO_SALT', 'COMBO_DOXY')):
                pans = []
                for p in params:
                    if p in self.figures:
                        tab_cols = []
                        if p in self.flag_widgets:
                            tab_cols.append(self.flag_widgets[p])
                        else:
                            tab_cols.append(Spacer(height=41))
                        tab_cols.append(self.figures[p])
                        tab = column(tab_cols)
                        pan = Panel(child=tab, title=pan_title(self.plot_parameters_mapping.get(p) or p))
                        pans.append(pan)
                columns.append(column([Tabs(tabs=pans)]))
        else:
            for p1 in ('x1', 'x2', 'x3'):
                columns.append(column([self.flag_widgets[p1], self.figures[p1]]))

        return columns

    def get_layout(self):
        tabs = self.get_tab_layout()
        meta_tabs = self.get_tabs(Data=['select_all_button', 'deselect_all_button', 'pressure_slider'],
                                  Metadata=['comnt_samp', 'comnt_visit', 'comnt_visit_button'],
                                  Import_Export=['file_button', 'download_button'],
                                  Info=['info_block'])
        std_parameter_tabs = self.get_std_parameter_tab_layout()
        widgets_1 = column([self.month_selector, self.spacer, self.selected_series], sizing_mode="fixed", height=300, width=200)
        widgets_2 = column([Spacer(width=125)], sizing_mode="fixed", height=10, width=125)
        widgets_3 = column([meta_tabs], sizing_mode="fixed", height=100, width=100)
        l = grid([row([self.map, widgets_1, widgets_2, widgets_3]),
                  row([*std_parameter_tabs,
                       column([tabs]),
                       ])],
                 )
        return l

    @property
    def spacer(self):
        return Spacer(height=10)

    def return_layout(self):
        """
        Return the layout in order to display in an Embedded bokeh server within a notebook
        :return:
        """
        return self.get_layout()

    def show_plot(self):
        """
        As a html-file or output_notebook
        :return:
        """
        l = self.get_layout()
        show(l)


if __name__ == '__main__':
    # path_zipfile = 'D:\\Utveckling\\Github\\ctdpy\\ctdpy\\exports\\SHARK_CTD_2018_IBT_SMHI.zip'
    path_zipfile = 'C:\\Utveckling\\ctdpy\\ctdpy\\tests\\etc\\SHARK_CTD_2018_BAS_SMHI.zip'

    # profile_name = 'ctd_profile_SBE09_0827_20180120_0910_26_01_0126'
    profile_name = 'ctd_profile_SBE09_1044_20181205_1536_34_01_0154'
    profile_name2 = 'ctd_profile_SBE09_1044_20181206_1139_34_01_0157'

    start_time = time.time()
    rzip = ReadZipFile(path_zipfile, profile_name)
    rzip2 = ReadZipFile(path_zipfile, profile_name2)
    print("Zipfile loaded--%.3f sec" % (time.time() - start_time))
    # print(rzip._df)

    data_parameter_list = ['PRES_CTD [dbar]',
                           'SALT_CTD [psu (PSS-78)]', 'SALT2_CTD [psu (PSS-78)]',
                           'TEMP_CTD [°C (ITS-90)]', 'TEMP2_CTD [°C (ITS-90)]',
                           'DOXY_CTD [ml/l]', 'DOXY2_CTD [ml/l]',
                           ]
    df_parameter_list = data_parameter_list + ['STATION', 'LATITUDE_DD', 'LONGITUDE_DD', 'YEAR', 'MONTH', 'DAY']
    # parameter_list = ['PRES_CTD [dbar]', 'CNDC_CTD [S/m]', 'CNDC2_CTD [S/m]', 'SALT_CTD [psu (PSS-78)]',
    #                   'SALT2_CTD [psu (PSS-78)]', 'TEMP_CTD [°C (ITS-90)]', 'TEMP2_CTD [°C (ITS-90)]',
    #                   'DOXY_CTD [ml/l]', 'DOXY2_CTD [ml/l]', 'PAR_CTD [µE/(cm2 ·sec)]', 'CHLFLUO_CTD [mg/m3]',
    #                   'TURB_CTD [NTU]', 'PHYC_CTD [ppb]']
    # parameter_list = ['PRES_CTD [dbar]','CNDC_CTD [mS/m]','CNDC2_CTD [mS/m]','SALT_CTD [psu]','SALT2_CTD [psu]',
    #                       'TEMP_CTD [°C]','TEMP2_CTD [°C]','DOXY_CTD [ml/l]','DOXY2_CTD [ml/l]',
    #                       'PAR_CTD [µE/(cm2 ·sec)]','CHLFLUO_CTD [mg/m3]','TURB_CTD [NTU]','PHYC_CTD [ppb]']

    start_time = time.time()
    data = rzip.get_data(df_parameter_list, astype=None)
    data2 = rzip2.get_data(df_parameter_list, astype=None)

    print("Data retrieved--%.3f sec" % (time.time() - start_time))
    #    data = rzip.get_dataframe()
    # print(data)
    data['key'] = data[['YEAR', 'MONTH', 'DAY', 'STATION']].apply(lambda x: '_'.join(x), axis=1)
    data2['key'] = data2[['YEAR', 'MONTH', 'DAY', 'STATION']].apply(lambda x: '_'.join(x), axis=1)

    data = data.append(data2).reset_index(drop=True)

    start_time = time.time()
    plot = QC_WorkTool(data, parameters=data_parameter_list)
    plot.set_map()
    plot.plot_stations()
    plot.plot_data()
    plot.show_plot()
    # plot.plot(x='TEMP_CTD [°C (ITS-90)]',
    #              y='PRES_CTD [dbar]',
    #              z='SALT_CTD [psu (PSS-78)]',
    #              name=profile_name)
    print("Data ploted--%.3f sec" % (time.time() - start_time))

    # start_time = time.time()
    # profile = ProfilePlot(data, parameters=parameter_list)
    # profile.plot(x='TEMP_CTD [°C (ITS-90)]',
    #              y='PRES_CTD [dbar]',
    #              z='SALT_CTD [psu (PSS-78)]',
    #              name=profile_name)
    # print("Data ploted--%.3f sec" % (time.time() - start_time))




