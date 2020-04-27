# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 13:19:50 2018

@author: a002028
"""

import time
import numpy as np
import pandas as pd
import zipfile
# from pprint import pprint
from bokeh.io import output_notebook
from bokeh.models import Button, FileInput, ColumnDataSource, Range1d, CustomJS, Div, WidgetBox, LinearAxis, Circle, TapTool, HoverTool, CrosshairTool, WheelZoomTool, ResetTool, PanTool, SaveTool,  LassoSelectTool, ColorBar, LinearColorMapper  # , LabelSet, Slider
from bokeh.layouts import grid, row, column, layout, gridplot, GridSpec, widgetbox, Spacer  # , layout, widgetbox
from bokeh.models.widgets import Select, RangeSlider, DataTable, TableColumn, Panel, Tabs
from bokeh.plotting import figure, show, output_file
from bokeh.tile_providers import get_provider, Vendors
from bokeh.events import ButtonClick
from bokeh.palettes import viridis   #  magma, viridis
from matplotlib import colors
from matplotlib import cm
import gsw
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

    return [color_array[int(d*2)] for d in dep_serie]


def convert_projection(lats, lons):
    """

    :param lats:
    :param lons:
    :return:
    """
    #TODO MOVE! this exists somewhere else too..
    import pyproj

    project_projection = pyproj.Proj("EPSG:4326")  # wgs84
    google_projection = pyproj.Proj("EPSG:3857")  # default google projection

    x, y = pyproj.transform(project_projection, google_projection, lats, lons)
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
    def month_selection_callback(position_source=None, position_plot_source=None):
        """"""
        code = """
        // Get data from ColumnDataSource
        var selected_data = {LATIT: [], LONGI: [], STATION: [], KEY: [], MONTH: []};
        var data = source.data;
        
        var month_mapping = {'All': 'All',
                             'January': '01', 'February': '02',
                             'March': '03', 'April': '04',
                             'May': '05', 'June': '06',
                             'July': '07', 'August': '08',
                             'September': '09', 'October': '10',
                             'November': '11', 'December': '12'};

        var selected_month = month_mapping[month.value];

        var key_val, lat_val, lon_val, statn_val, mon_val;
        for (var i = 0; i < data.KEY.length; i++) {
            key_val = data.KEY[i];
            lat_val = data.LATIT[i];
            lon_val = data.LONGI[i];
            statn_val = data.STATION[i];
            mon_val = data.MONTH[i];

            if (selected_month == 'All') {
                selected_data.KEY.push(key_val);
                selected_data.LATIT.push(lat_val);
                selected_data.LONGI.push(lon_val);
                selected_data.STATION.push(statn_val);
                selected_data.MONTH.push(mon_val);
            } else if (mon_val == selected_month) {
                selected_data.KEY.push(key_val);
                selected_data.LATIT.push(lat_val);
                selected_data.LONGI.push(lon_val);
                selected_data.STATION.push(statn_val);
                selected_data.MONTH.push(mon_val);
            }
        }
        
        plot_source.data = selected_data;
        """
        # Create a CustomJS callback with the code and the data
        return CustomJS(args={'source': position_source,
                              'plot_source': position_plot_source},
                        code=code)

    @staticmethod
    def station_callback(position_source=None, data_source=None,
                         temp_obj=None, salt_obj=None, doxy_obj=None,
                         seconds=None):
        """
        'title': fig.title, 'text_input': text_input},
        code="title.text = text_input.value"

        """
        # assert position_source, data_source
        code = """
        // Set column name to select similar glyphs
        var key = 'KEY';
        var statn_key = 'STATION';
        var sec = seconds.data;

        // Get data from ColumnDataSource
        var position_data = position_source.data;
        var data = data_source.data;

        // Get indices array of all selected items
        var selected = position_source.selected.indices;

        // Update figure titlesflag_color_mapping 
        var station_name = position_data[statn_key][selected[0]];
        var selected_key = position_data[key][selected[0]];
        
        temp_obj.title.text = station_name + ' - ' + selected_key
        salt_obj.title.text = station_name + ' - ' + selected_key
        doxy_obj.title.text = station_name + ' - ' + selected_key

        // Update active keys in data source 
        data['x1'] = data[selected_key+'_TEMP_CTD [°C (ITS-90)]'];
        data['x1_q0'] = data[selected_key+'_Q0_TEMP_CTD'];
        data['color_x1'] = data[selected_key+'_color_x1'];
        if ('x1b' in data) {
            data['x1b'] = data[selected_key+'_TEMP2_CTD [°C (ITS-90)]'];
            data['color_x1b'] = data[selected_key+'_color_x1b'];
        }

        data['x2'] = data[selected_key+'_SALT_CTD [psu (PSS-78)]'];
        data['x2_q0'] = data[selected_key+'_Q0_SALT_CTD'];
        data['color_x2'] = data[selected_key+'_color_x2'];
        if ('x2b' in data) {
            data['x2b'] = data[selected_key+'_SALT2_CTD [psu (PSS-78)]'];
            data['color_x2b'] = data[selected_key+'_color_x2b'];
        }
        
        data['x3'] = data[selected_key+'_DOXY_CTD [ml/l]'];
        data['x3_q0'] = data[selected_key+'_Q0_DOXY_CTD'];
        data['color_x3'] = data[selected_key+'_color_x3'];
        if ('x3b' in data) {
            data['x3b'] = data[selected_key+'_DOXY2_CTD [ml/l]'];
            data['color_x3b'] = data[selected_key+'_color_x3b'];
        }
        
        data['y'] = data[selected_key+'_PRES_CTD [dbar]'];

        // Save changes to ColumnDataSource
        data_source.change.emit();
        
        var d = new Date();
        var t = d.getTime();
        var new_seconds = Math.round(t / 1000);
        sec.tap_time[0] = new_seconds;
        sec.reset_time[0] = new_seconds;
        seconds.change.emit();
        temp_obj.reset.emit();
        salt_obj.reset.emit();
        doxy_obj.reset.emit();
        //console.log('new_seconds', new_seconds)
        //console.log('sec.tap_time[0]', sec.tap_time[0])
        """
        # Create a CustomJS callback with the code and the data
        return CustomJS(args={'position_source': position_source,
                              'data_source': data_source,
                              'temp_obj': temp_obj,
                              'salt_obj': salt_obj,
                              'doxy_obj': doxy_obj,
                              'seconds': seconds,
                              },
                        code=code)

    @staticmethod
    def lasso_callback(monthly_keys=None, in_data=None, plot_data=None, x_range=None, y_range=None):
        """"""
        code = """
        
        var month_mapping = {'All': 'All',
                             'January': '01', 'February': '02',
                             'March': '03', 'April': '04',
                             'May': '05', 'June': '06',
                             'July': '07', 'August': '08',
                             'September': '09', 'October': '10',
                             'November': '11', 'December': '12'};

        var selected_month = month_mapping[month.value];
        
        var data = {x: [], y: [], color: []};
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
    def get_flag_widget(position_source, data_source, flag_key=None, color_key=None):
        """"""
        code = """
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
    def get_flag_buttons_widget(position_source, data_source, flag_key=None, color_key=None, figure_objs=None):
        """"""
        code = """
        var flag_color_mapping = {'A-flag': {'c':'navy', 'flag': ''},
                                  'B-flag': {'c':'red', 'flag': 'B'},
                                  'E-flag': {'c':'green', 'flag': 'E'},
                                  'S-flag': {'c':'orange', 'flag': 'S'}};

        // Get data from ColumnDataSource
        var position_data = position_source.data;
        var data = data_source.data;

        // Set variables attributes
        var color_column = color_key;
        var selected_flag = flag;

        var selected_position = position_source.selected.indices;
        var selected_key = position_data['KEY'][selected_position[0]];
        var flag_column = selected_key+'_'+flag_key;

        // Get indices array of all selected items
        var selected_indices = data_source.selected.indices;

        for (var i = 0; i < selected_indices.length; i++) {
            data[color_column][selected_indices[i]] = flag_color_mapping[selected_flag]['c'];
            data[flag_column][selected_indices[i]] = flag_color_mapping[selected_flag]['flag'];
        }

        // Save changes to ColumnDataSource
        data_source.change.emit();
        for (var i = 0; i < figure_objs.length; i++) {
            figure_objs[i].reset.emit();
        }
        """
        # button_types = default, primary, success, warning or danger
        button_types = ['primary', 'danger', 'success', 'warning']
        flag_list = ['A-flag', 'B-flag', 'E-flag', 'S-flag']
        button_list = [Spacer(width=10)]

        for flag, b_type in zip(flag_list, button_types):
            callback = CustomJS(args={'position_source': position_source,
                                      'data_source': data_source,
                                      'figure_objs': figure_objs,
                                      'flag': flag},
                                code=code)

            callback.args["color_key"] = color_key
            callback.args["flag_key"] = flag_key
            button = Button(label=flag, width=30, button_type=b_type)
            button.js_on_event(ButtonClick, callback)
            button_list.append(button)
        button_list.append(Spacer(width=10))
        return row(button_list, sizing_mode="stretch_width")

    @staticmethod
    def get_download_widget():
        """"""
        button = Button(label="Download selected data", button_type="success", width=40)
        return button

    @staticmethod
    def get_file_widget():
        # button_input = FileInput(accept=".csv,.txt")
        button_input = FileInput()

        return button_input

    @staticmethod
    def add_hlinked_crosshairs(fig1, fig2, fig3):
        cross1 = CrosshairTool(line_alpha=0.5)
        cross2 = CrosshairTool(line_alpha=0.5)
        cross3 = CrosshairTool(line_alpha=0.5)
        fig1.add_tools(cross1)
        fig2.add_tools(cross2)
        fig3.add_tools(cross3)
        js_move = """
        cross_a.spans.width.computed_location = cb_obj.sy;
        cross_b.spans.width.computed_location = cb_obj.sy;
        current_cross.spans.height.computed_location = null;
        """
        js_leave = """
        cross_a.spans.width.computed_location = null;
        cross_b.spans.width.computed_location = null;
        """
        args = {'current_cross': cross1, 'cross_a': cross2, 'cross_b': cross3, 'fig': fig2}
        fig1.js_on_event('mousemove', CustomJS(args=args, code=js_move))
        fig1.js_on_event('mouseleave', CustomJS(args=args, code=js_leave))

        args = {'current_cross': cross2, 'cross_a': cross1, 'cross_b': cross3, 'fig': fig3}
        fig2.js_on_event('mousemove', CustomJS(args=args, code=js_move))
        fig2.js_on_event('mouseleave', CustomJS(args=args, code=js_leave))

        args = {'current_cross': cross3, 'cross_a': cross1, 'cross_b': cross2, 'fig': fig1}
        fig3.js_on_event('mousemove', CustomJS(args=args, code=js_move))
        fig3.js_on_event('mouseleave', CustomJS(args=args, code=js_leave))

    @staticmethod
    def render_callback(source=None, x_range_dict=None):
        """"""
        return CustomJS(args={'source': source, 'xr': x_range_dict}, code="""
                var geometry = cb_data['geometry'];
                var y_data = geometry.y; // current mouse y position in plot coordinates
                //console.log("(,y)=", y_data)
                var data = {'tempx': [xr.xr_temp.start, xr.xr_temp.end], 
                            'saltx': [xr.xr_salt.start, xr.xr_salt.end], 
                            'doxyx': [xr.xr_doxy.start, xr.xr_doxy.end], 
                            'y': [y_data, y_data]};
                source.data = data;
                cb_obj.reset.emit();
            """)

    @staticmethod
    def x_range_callback(x_range_obj=None, delta=4, seconds=None):
        code = """
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
        var sec = seconds.data;
        var d = new Date();
        var t = d.getTime();
        sec.reset_time[0] = t / 1000;
        //console.log('sec.reset_time[0]', sec.reset_time[0])
        seconds.change.emit();
        """
        return CustomJS(args={'seconds': seconds},
                        code=code)


class QCPlot(CallBacks):
    """
    """
    def __init__(self, dataframe, parameters=None, color_fields=None, qflag_fields=None, auto_q_flag_parameters=None,
                 tabs=None, plot_parameters_mapping=None, output_filename="CTD_QC_VIZ.html", output_as_notebook=False):
        super().__init__()
        self.seconds = ColumnDataSource(data=dict(tap_time=[None], reset_time=[None]))

        self.map = None
        self.df = dataframe
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

        self.temp = figure(tools="pan,reset,wheel_zoom,lasso_select,save", active_drag="lasso_select",
                           title="", height=400, width=400,
                           tooltips=[("Temperature", "@x1 °C"),
                                     ("Depth", "@y m"),
                                     ("Auto-QC", "@x1_q0")])
        self.temp.title.align = 'center'
        self.temp.xaxis.axis_label = 'Temperature (°C)'
        self.temp.xaxis.axis_label_text_font_style = 'bold'
        self.temp.yaxis.axis_label = 'Depth (m)'
        self.temp.yaxis.axis_label_text_font_style = 'bold'
        # p.xgrid.grid_line_color = None
        self.temp.ygrid.band_fill_alpha = 0.05
        self.temp.ygrid.band_fill_color = "black"
        xrange_temp_callback = self.x_range_callback(x_range_obj=self.temp.x_range, seconds=self.seconds)
        self.temp.x_range.js_on_change('start', xrange_temp_callback)
        self.temp.js_on_event('reset', self.reset_callback(self.seconds), xrange_temp_callback)
        self.temp.toolbar.active_scroll = self.temp.select_one(WheelZoomTool)

        self.salt = figure(tools="pan,reset,wheel_zoom,lasso_select,save",  active_drag="lasso_select",
                           title="", height=400, width=400, y_range=self.temp.y_range,
                           tooltips=[("Salinity", "@x2 psu"),
                                     ("Depth", "@y m"),
                                     ("Auto-QC", "@x2_q0")])
        self.salt.title.align = 'center'
        self.salt.xaxis.axis_label = 'Salinity (PSU)'
        self.salt.xaxis.axis_label_text_font_style = 'bold'
        self.salt.ygrid.band_fill_alpha = 0.05
        self.salt.ygrid.band_fill_color = "black"
        xrange_salt_callback = self.x_range_callback(x_range_obj=self.salt.x_range, seconds=self.seconds)
        self.salt.x_range.js_on_change('start', xrange_salt_callback)
        self.salt.js_on_event('reset', self.reset_callback(self.seconds), xrange_salt_callback)
        self.salt.toolbar.active_scroll = self.salt.select_one(WheelZoomTool)

        self.doxy = figure(tools="pan,reset,wheel_zoom,lasso_select,save",  active_drag="lasso_select",
                           title="", height=400, width=400, y_range=self.temp.y_range,
                           tooltips=[("Oxygen", "@x3 ml/l"),
                                     ("Depth", "@y m"),
                                     ("Auto-QC", "@x3_q0")])
        self.doxy.title.align = 'center'
        self.doxy.xaxis.axis_label = 'Oxygen (ml/l)'
        self.doxy.xaxis.axis_label_text_font_style = 'bold'
        self.doxy.ygrid.band_fill_alpha = 0.05
        self.doxy.ygrid.band_fill_color = "black"
        xrange_doxy_callback = self.x_range_callback(x_range_obj=self.doxy.x_range, delta=3, seconds=self.seconds)
        self.doxy.x_range.js_on_change('start', xrange_doxy_callback)
        self.doxy.js_on_event('reset', self.reset_callback(self.seconds), xrange_doxy_callback)
        self.doxy.toolbar.active_scroll = self.doxy.select_one(WheelZoomTool)

        self.add_hlinked_crosshairs(self.temp, self.salt, self.doxy)

        self.ts = figure(tools="pan,reset,wheel_zoom,lasso_select,save", title="CTD TS Diagram", x_range=(2, 36), y_range=(-2, 20), height=400, width=400)
        self.ts.title.align = 'center'

        self._setup_position_source()
        self._setup_data_source()
        self._setup_TS_source()
        self._setup_month_selector()
        self._setup_flag_widgets()
        self._setup_download_button()
        self._setup_get_file_button()
        self._setup_serie_table()
        self._setup_map()

        self.ts_axis_ranges = {'t_min': 0, 't_max': 25, 's_min': 2, 's_max': 36}

    @staticmethod
    def _get_monthly_keys(position_df):
        """"""
        # FIXME Is this really necessary ?
        dictionary = {'All': position_df['KEY'].to_list()}
        for month in [str(m).zfill(2) for m in range(1, 13)]:
            boolean = position_df['MONTH'] == month
            dictionary[month] = position_df.loc[boolean, 'KEY'].to_list()
        return dictionary

    def _setup_position_source(self):
        """
        :return:
        """
        position_df = self.df[['STATION', 'LATITUDE_DD', 'LONGITUDE_DD', 'KEY', 'MONTH']].drop_duplicates(
            keep='first').reset_index(drop=True)
        xs, ys = convert_projection(position_df['LATITUDE_DD'].astype(float).values, position_df['LONGITUDE_DD'].astype(float).values)
        position_df['LONGI'] = xs
        position_df['LATIT'] = ys
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
                                     width=120)
        # self.month_selector.js_event_callbacks('value', callback)
        self.month_selector.js_on_change('value', callback)
        # self.month_selector.title.text_align = 'center'
        callback.args["month"] = self.month_selector

    def _setup_download_button(self):
        """"""
        self.download_button = self.get_download_widget()

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
                                         width=300, height=370)

    def _setup_flag_widgets(self):
        """
        Options:
        self.get_flag_widget(*args, **kwargs)
        self.get_flag_buttons_widget(*args, **kwargs)
        """
        self.widget_temp = self.get_flag_buttons_widget(self.position_plot_source, self.data_source, figure_objs=[self.temp, self.salt, self.doxy],
                                                        flag_key='Q_TEMP_CTD',
                                                        color_key='color_x1')

        self.widget_salt = self.get_flag_buttons_widget(self.position_plot_source, self.data_source, figure_objs=[self.temp, self.salt, self.doxy],
                                                        flag_key='Q_SALT_CTD',
                                                        color_key='color_x2')

        self.widget_doxy = self.get_flag_buttons_widget(self.position_plot_source, self.data_source, figure_objs=[self.temp, self.salt, self.doxy],
                                                        flag_key='Q_DOXY_CTD',
                                                        color_key='color_x3')

    def _setup_TS_source(self):
        """
        :return:
        """
        params = self.parameters + ['KEY']
        ts_df = self.df[params]
        ts_df['x'] = ts_df[self.plot_parameters_mapping.get('x2')]  # x2 = SALT
        ts_df['y'] = ts_df[self.plot_parameters_mapping.get('x1')]  # x1 = TEMP
        ts_df['color'] = get_color_palette(dep_serie=ts_df[self.plot_parameters_mapping.get('y')])
        self.ts_source = ColumnDataSource(data=ts_df)
        self.ts_plot_source = ColumnDataSource(data=dict(x=[], y=[], color=[]))

    def _setup_data_source(self):
        """
        :return:
        """
        print('Setting up data source structure...')
        # self.df[self.parameters] = self.df[self.parameters].astype(float)
        data_dict = {}
        for key in self.position_source.data['KEY']:
            data_boolean = self.df['KEY'] == key
            for parameter in self.parameters + self.color_fields + self.qflag_fields + self.auto_qflag_fields:
                data_key = '_'.join((key, parameter))
                data_dict[data_key] = self.df.loc[data_boolean, parameter].values

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

    def _setup_map(self):
        """"""

        pan = PanTool()
        save = SaveTool()
        tap = TapTool()
        lasso = LassoSelectTool()
        reset = ResetTool()
        wheel = WheelZoomTool()

        tooltips = HoverTool(tooltips=[("Station", "@STATION"),
                                       # ("Date", "@SDATE"),
                                       ("Serie", "@KEY")])

        # range bounds supplied in web mercator coordinates
        self.map = figure(x_range=(0, 4000000), y_range=(7100000, 9850000),
                          x_axis_type="mercator", y_axis_type="mercator", height=400, width=1210,
                          tools=[pan, wheel, tap, lasso, tooltips, reset, save])

        self.map.yaxis.axis_label = ' '  # in order to aline y-axis with figure window below
        self.map.toolbar.active_scroll = self.map.select_one(WheelZoomTool)
        self.map.add_tile(self.tile_provider)

        tap.callback = self.station_callback(position_source=self.position_plot_source,
                                             data_source=self.data_source,
                                             temp_obj=self.temp,
                                             salt_obj=self.salt,
                                             doxy_obj=self.doxy,
                                             seconds=self.seconds)

        # When we mark stations on the map using lasso selection, we activate the TS-diagram.
        lasso_callback = self.lasso_callback(monthly_keys=self.monthly_keys,
                                             in_data=self.ts_source,
                                             plot_data=self.ts_plot_source,
                                             x_range=self.ts.x_range,
                                             y_range=self.ts.y_range)
        lasso_callback.args["month"] = self.month_selector
        self.position_plot_source.selected.js_on_change('indices', lasso_callback)

    def plot_stations(self):
        """"""
        renderer = self.map.circle('LONGI', 'LATIT', source=self.position_plot_source,
                                   color="#5BC798", line_color="aquamarine", size=10, alpha=0.7)

        selected_circle = Circle(fill_alpha=0.5, fill_color="red", line_color="aquamarine")
        nonselected_circle = Circle(fill_alpha=0.2, fill_color="blue", line_color="aquamarine")

        renderer.selection_glyph = selected_circle
        renderer.nonselection_glyph = nonselected_circle

    def plot_data(self):
        """"""

        # Temperature figure
        self.temp.line('x1', 'y', color="color_x1", line_color="navy", line_width=1, alpha=0.3, source=self.data_source)
        self.temp.circle('x1', 'y', color="color_x1", line_color="white", size=6, alpha=0.5, source=self.data_source, legend_label='Sensor 1')
        # self.temp.line('tempx', 'y', line_color="black", line_width=1, alpha=0.5, source=self.render_source)
        if 'x1b' in self.plot_parameters_mapping:
            self.temp.circle('x1b', 'y', color="color_x1b", line_color="white", size=6, alpha=0.5, source=self.data_source, legend_label='Sensor 2')
            self.temp.legend.location = "top_left"
            self.temp.legend.click_policy = "hide"
        else:
            self.temp.legend.visible = False
        self.temp.y_range.flipped = True

        # Salinity figure
        self.salt.line('x2', 'y', color="color_x2", line_color="navy", line_width=1, alpha=0.3, source=self.data_source)
        self.salt.circle('x2', 'y', color="color_x2", line_color="white", size=6, alpha=0.5, source=self.data_source, legend_label='Sensor 1')
        # self.salt.line('saltx', 'y', line_color="black", line_width=1, alpha=0.5, source=self.render_source)
        if 'x2b' in self.plot_parameters_mapping:
            self.salt.circle('x2b', 'y', color="color_x2b", line_color="white", size=6, alpha=0.5, source=self.data_source, legend_label='Sensor 2')
            self.salt.legend.location = "top_left"
            self.salt.legend.click_policy = "hide"
        else:
            self.salt.legend.visible = False
        self.salt.y_range.flipped = True

        # Oxygen figure
        self.doxy.line('x3', 'y', color="color_x3", line_color="navy", line_width=1, alpha=0.3, source=self.data_source)
        self.doxy.circle('x3', 'y', color="color_x3", line_color="white", size=6, alpha=0.5, source=self.data_source, legend_label='Sensor 1')
        # self.doxy.line('doxyx', 'y', line_color="black", line_width=1, alpha=0.5, source=self.render_source)
        if 'x3b' in self.plot_parameters_mapping:
            self.doxy.circle('x3b', 'y', color="color_x3b", line_color="white", size=6, alpha=0.5, source=self.data_source, legend_label='Sensor 2')
            self.doxy.legend.location = "top_left"
            self.doxy.legend.click_policy = "hide"
        else:
            self.doxy.legend.visible = False
        self.doxy.y_range.flipped = True

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

    def show_plot(self):
        # if self.output_as_notebook:
        #     widgets_1 = column([self.selected_series], sizing_mode="fixed", height=370, width=200)
        #     widgets_2 = column([Spacer(width=125)], sizing_mode="fixed", height=10, width=125)
        #     widgets_3 = column([self.month_selector,
        #                         Spacer(height=10),
        #                         self.file_button,
        #                         Spacer(height=10),
        #                         self.download_button],
        #                        sizing_mode="fixed", height=100, width=100)
        #     l = grid([row([self.map]),
        #               row([widgets_1, widgets_2, widgets_3]),
        #               row([column([self.widget_temp, self.temp]),
        #                    column([self.widget_salt, self.salt])]),
        #               row([column([self.widget_doxy, self.doxy]),
        #                    column([Spacer(height=20), self.ts])])],  # self.ts
        #              sizing_mode='stretch_width'
        #              )
        # else:
        if 1:
            widgets_1 = column([self.selected_series], sizing_mode="fixed", height=370, width=200)
            widgets_2 = column([Spacer(width=125)], sizing_mode="fixed", height=10, width=125)
            widgets_3 = column([self.month_selector,
                                Spacer(height=10),
                                self.file_button,
                                Spacer(height=10),
                                self.download_button],
                               sizing_mode="fixed", height=100, width=100)
            l = grid([row([self.map, widgets_1, widgets_2, widgets_3]),
                      row([column([self.widget_temp, self.temp]),
                           column([self.widget_salt, self.salt]),
                           column([self.widget_doxy, self.doxy]),
                           column([Spacer(height=20), self.ts])])],  # self.ts
                     sizing_mode='stretch_width'
                     )

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
    plot = QCPlot(data, parameters=data_parameter_list)
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




