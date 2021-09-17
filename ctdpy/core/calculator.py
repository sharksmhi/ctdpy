# -*- coding: utf-8 -*-
"""
Created on 2019-11-06 08:27

@author: a002028

"""
import gsw
import numpy as np
from ctdpy.core import utils


class Depth:
    """Handler for the depth parameter. Consider density, pressure and latitude when calculating true depth."""

    def __init__(self):
        """Set default values to class properties."""
        self._true_depth = None
        self._latitude = None
        self._density = None
        self._gravity = None
        self._pressure = None

    def calculate_true_depth(self):
        """Calculate true depth."""
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
            depth_list.append(utils.round_value(sum(water_package_height)))

            pres_0 = pres
            dens_0 = dens

        self.true_depth = list(map(str, depth_list))

    def set_attributes(self, attr_dictionary=None):
        """Set class attribute."""
        attr_dictionary = attr_dictionary or {}
        for attr, value in attr_dictionary.items():
            setattr(self, attr, value)

    @property
    def true_depth(self):
        """Return true depth."""
        return self._true_depth

    @true_depth.setter
    def true_depth(self, depth_list):
        """Set the true_depth property."""
        self._true_depth = depth_list

    @property
    def density(self):
        """Return density."""
        return self._density

    @density.setter
    def density(self, density_series):
        """Set the density property."""
        if density_series[0] < 100:
            # input equals Sigma-T (density - 1000)
            self._density = density_series + 1000
        else:
            self._density = density_series

    @property
    def pressure(self):
        """Return pressure."""
        return self._pressure

    @pressure.setter
    def pressure(self, pressure_series):
        """Set the pressure property."""
        if pressure_series[1] < 1000:
            # value for index 0 might be 0 dbar, therefor index 1
            # input unit equals dbar
            # output unit equals Pascal (1 dbar = 10000 Pa)
            self._pressure = pressure_series * 10000
        else:
            self._pressure = pressure_series

    @property
    def latitude(self):
        """Return latitude."""
        return self._latitude

    @latitude.setter
    def latitude(self, latitude_value):
        """Set the latitude property."""
        if isinstance(latitude_value, str):
            latitude_value = latitude_value.replace('N', '').replace(' ', '')
        self._latitude = utils.decmin_to_decdeg(latitude_value)

    @property
    def gravity(self):
        """Return gravity."""
        return self._gravity

    @gravity.setter
    def gravity(self, pressure_series):
        """Set the gravity property based on the gsw.grav function.

        Args:
            pressure_series: pressure with unit [dbar]
        """
        self._gravity = gsw.grav(self.latitude, pressure_series)


class Calculator:
    """Calculate true depth."""

    def update_dataframe(self, new_df):
        """Reset dataframe."""
        self.df = new_df

    @staticmethod
    def get_true_depth(attribute_dictionary=None):
        """Return true depth."""
        if attribute_dictionary is None:
            attribute_dictionary = {}
        depth_calculator = Depth()
        depth_calculator.set_attributes(attribute_dictionary)
        depth_calculator.calculate_true_depth()

        return depth_calculator.true_depth
