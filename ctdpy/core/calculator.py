# -*- coding: utf-8 -*-
"""
Created on 2019-11-06 08:27

@author: a002028

"""
import gsw
import numpy as np

import utils


class Depth(object):
    """

    """
    def __init__(self):
        self._true_depth = None
        self._latitude = None
        self._density = None
        self._gravity = None
        self._pressure = None

    def calculate_true_depth(self):
        """
        :return:
        """
        water_package_height = []
        depth_list = []

        pres_0 = 0
        dens_0 = self.density[0]

        for pres, dens, grav in zip(self.pressure, self.density, self.gravity):

            # Pressure step
            pres_1 = (pres - pres_0)

            # Mean density for water package.
            dens_1 = np.mean((dens_0, dens))

            # Water package height depending on mean density and pressure step (usually 0.5-1.0 dbar for hi resolution
            # CTD-data)
            height = pres_1 / (grav * dens_1)

            # add current calculated water package height and sum up height list
            water_package_height.append(height)
            depth_list.append(sum(water_package_height))

            pres_0 = pres
            dens_0 = dens

        self.true_depth = list(map(str, depth_list))

    def set_attributes(self, attr_dictionary={}):
        """
        :param attr_dictionary:
        :return:
        """
        for attr, value in attr_dictionary.items():
            print(attr, value)
            setattr(self, attr, value)

    @property
    def true_depth(self):
        return self._true_depth

    @true_depth.setter
    def true_depth(self, depth_list):
        self._true_depth = depth_list

    @property
    def density(self):
        return self._density

    @density.setter
    def density(self, density_series):
        if density_series[0] < 100:
            # input equals Sigma-T (density - 1000)
            self._density = density_series + 1000
        else:
            self._density = density_series

    @property
    def pressure(self):
        return self._pressure

    @pressure.setter
    def pressure(self, pressure_series):
        if pressure_series[1] < 1000:
            # value for index 0 might be 0 dbar
            # input unit equals dbar
            self._pressure = pressure_series * 10000
        else:
            self._pressure = pressure_series

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, latitude_value):
        if isinstance(latitude_value, str):
            latitude_value = latitude_value.replace('N', '').replace(' ', '')
        self._latitude = utils.decmin_to_decdeg(latitude_value)

    @property
    def gravity(self):
        return self._gravity

    @gravity.setter
    def gravity(self, pressure_series):
        """
        :param pressure_series: pressure with unit [dbar]
        :return:
        """
        self._gravity = gsw.grav(self.latitude, pressure_series)


class Calculator(object):
    """

    """
    def update_dataframe(self, new_df):
        """
        :param new_df:
        :return:
        """
        self.df = new_df

    def get_true_depth(self, attribute_dictionary={}):
        """
        :return:
        """
        depth_calculator = Depth()
        depth_calculator.set_attributes(attribute_dictionary)
        depth_calculator.calculate_true_depth()

        return depth_calculator.true_depth
