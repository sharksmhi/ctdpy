# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 13:19:50 2018

@author: a002028
"""

import numpy as np
import pandas as pd
import zipfile
from bokeh.io import output_notebook
from bokeh.models import ColumnDataSource, CustomJS, WidgetBox, LinearAxis
from bokeh.layouts import row, column
from bokeh.models.widgets import Select, RangeSlider, DataTable, TableColumn
from bokeh.plotting import figure, show, output_file
from bokeh.tile_providers import get_provider, Vendors
from bokeh.palettes import viridis
from matplotlib import colors
from matplotlib import cm
import gsw


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
