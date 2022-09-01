# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 11:18:06 2018

@author: a002028
"""
import six
from abc import ABCMeta
from ctdpy.core import utils


class BaseFileHandler(six.with_metaclass(ABCMeta, object)):
    """BaseClass to hold various methods for loading different types of files.

    Can be settings files, data files, info files, etc.
    Holds properties and their setters
    (perhaps we should move this to a "BaseProperties"?)
    """

    def __init__(self, settings):
        """Initialize and set properies to None."""
        super().__init__()
        self.class_methods = utils.get_method_dictionary(BaseFileHandler)
        self.settings = settings
        self.filename = ''
        self._station = None
        self._cruise = None
        self._longitude_dd = None
        self._latitude_dd = None
        self._year = None
        self._month = None
        self._day = None
        self._hour = None
        self._minute = None
        self._second = None

    def __str__(self):
        """Customize __str__."""
        return "<{}: '{}'>".format(self.__class__.__name__, self.filename)

    def __repr__(self):
        """Customize __repr__."""
        return str(self)

    def get_property_value(self, key):
        """Get value from property of self.

        Args:
            key: Intended to be the name of a property method of self.
        """
        # FIXME Perhaps we need to check aginst .__class__.__name__
        #  attributes in order to exclude child class attributes..
        # FIXME if so: use self.class_methods
        return getattr(self, key.lower(), '')

    @property
    def station(self):
        """Return station."""
        return self._station

    @station.setter
    def station(self, name):
        """Set the station property with capital letters."""
        self._station = name.upper()

    @property
    def cruise(self):
        """Return cruise."""
        return self._cruise

    @cruise.setter
    def cruise(self, cruise_list):
        """Set the station property with capital letters.

        Cruise name according to Year_ShipCode_CruiseNumber ('NNNN_LLLL_NN')

        Args:
            cruise_list (iterable): (year, shipc, cruise_no)
        """
        self._cruise = '_'.join(cruise_list)

    @property
    def longitude_dd(self):
        """Return longitude_dd."""
        return self._longitude_dd

    @longitude_dd.setter
    def longitude_dd(self, longitude):
        """Set the longitude property in DD.dddd (Decimal degrees)."""
        if len(longitude.split('.')[0]) > 2:
            self._longitude_dd = utils.decmin_to_decdeg(longitude)
        else:
            self._longitude_dd = longitude

    @property
    def latitude_dd(self):
        """Return latitude_dd."""
        return self._latitude_dd

    @latitude_dd.setter
    def latitude_dd(self, latitude):
        """Set the latitude property in DD.dddd (Decimal degrees)."""
        if len(latitude.split('.')[0]) > 2:
            self._latitude_dd = utils.decmin_to_decdeg(latitude)
        else:
            self._latitude_dd = latitude

    @property
    def year(self):
        """Return year."""
        return self._year

    @year.setter
    def year(self, datetime_obj):
        """Set year."""
        self._year = datetime_obj.strftime('%Y')

    @property
    def month(self):
        """Return month."""
        return self._month

    @month.setter
    def month(self, datetime_obj):
        """Set month."""
        self._month = datetime_obj.strftime('%m')

    @property
    def day(self):
        """Return day."""
        return self._day

    @day.setter
    def day(self, datetime_obj):
        """Set day."""
        self._day = datetime_obj.strftime('%d')

    @property
    def hour(self):
        """Return hour."""
        return self._hour

    @hour.setter
    def hour(self, datetime_obj):
        """Set hour."""
        self._hour = datetime_obj.strftime('%H')

    @property
    def minute(self):
        """Return minute."""
        return self._minute

    @minute.setter
    def minute(self, datetime_obj):
        """Set minute."""
        self._minute = datetime_obj.strftime('%M')

    @property
    def second(self):
        """Return second."""
        return self._second

    @second.setter
    def second(self, datetime_obj):
        """Set second."""
        self._second = datetime_obj.strftime('%S')
