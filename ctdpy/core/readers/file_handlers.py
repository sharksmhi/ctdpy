# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 11:18:06 2018

@author: a002028
"""
from abc import ABCMeta
import six
from core import utils


class BaseFileHandler(six.with_metaclass(ABCMeta, object)):
    """ BaseClass to hold various methods for loading different types of files
        Can be settings files, data files, info files..

        Holds properties and their setters (perhaps we should move this to a "BaseProperties"?)
    """
    def __init__(self, settings):
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
        """ """
        return "<{}: '{}'>".format(self.__class__.__name__, self.filename)

    def __repr__(self):
        """ """
        return str(self)

    def get_dataset(self, dataset_id, ds_info, out=None,
                    xslice=slice(None), yslice=slice(None)):
        raise NotImplementedError

    def get_bounding_box(self):
        """Get the bounding box of the files, as a (lons, lats) tuple.

        The tuple return should a lons and lats list of coordinates traveling
        clockwise around the points available in the file.
        """
        raise NotImplementedError

    def get_property_value(self, key):
        """
        :param key: Intended to be the name of a property method
        :return: return of property method
        """
        #FIXME Perhaps we need to check aginst .__class__.__name__ attributes in order to exclude child class attributes..
        #FIXME if so: use self.class_methods
        return getattr(self, key.lower(), '')

    @property
    def station(self):
        """
        :return: Station name with capital letters
        """
        return self._station

    @station.setter
    def station(self, s):
        """
        Setter of station
        :param s: station name
        :return: Sets station name with capital letters
        """
        self._station = s.upper()

    @property
    def cruise(self):
        """
        :return: str, Cruise name according to Year_ShipCode_CruiseNumber ('NNNN_LLLL_NN')
        """
        return self._cruise

    @cruise.setter
    def cruise(self, cruise_list):
        """
        Setter of cruise
        :param cruise_list: tuple, (year, shipc, cruise_no)
        """
        self._cruise = '_'.join(cruise_list)

    @property
    def longitude_dd(self):
        """
        :return: Longitude in DD.dddd (Decimal degrees)
        """
        return self._longitude_dd

    @longitude_dd.setter
    def longitude_dd(self, l):
        """
        Setter of longitude_dd
        :param l: str
        """
        if len(l.split('.')[0]) > 2:
            self._longitude_dd = utils.decmin_to_decdeg(l)
        else:
            self._longitude_dd = l

    @property
    def latitude_dd(self):
        """
        :return: latitude in DD.dddd (Decimal degrees)
        """
        return self._latitude_dd

    @latitude_dd.setter
    def latitude_dd(self, l):
        """
        Setter of longitude_dd
        :param l: str
        """
        if len(l.split('.')[0]) > 2:
            self._latitude_dd = utils.decmin_to_decdeg(l)
        else:
            self._latitude_dd = l

    @property
    def year(self):
        """
        :return: str, YYYY
        """
        return self._year

    @year.setter
    def year(self, datetime_obj):
        """
        Setter of year
        """
        self._year = datetime_obj.strftime('%Y')

    @property
    def month(self):
        """
        :return: str, MM
        """
        return self._month

    @month.setter
    def month(self, datetime_obj):
        """
        Setter of month
        """
        self._month = datetime_obj.strftime('%m')

    @property
    def day(self):
        """
        :return: str, DD
        """
        return self._day

    @day.setter
    def day(self, datetime_obj):
        """
        Setter of day
        """
        self._day = datetime_obj.strftime('%d')

    @property
    def hour(self):
        """
        :return: str, HH
        """
        return self._hour

    @hour.setter
    def hour(self, datetime_obj):
        """
        Setter of hour
        """
        self._hour = datetime_obj.strftime('%H')

    @property
    def minute(self):
        """
        :return: str, MM
        """
        return self._minute

    @minute.setter
    def minute(self, datetime_obj):
        """
        Setter of minute
        """
        self._minute = datetime_obj.strftime('%M')

    @property
    def second(self):
        """
        :return: str, SS
        """
        return self._second

    @second.setter
    def second(self, datetime_obj):
        """
        Setter of second
        """
        self._second = datetime_obj.strftime('%S')


class BaseReader(object):
    """
    """
    def __init__(self, settings):
        self.settings = settings

    def _extract_info(self):
        raise NotImplementedError
#        for ds in self.file_info[]

    def get_reader(self):
        raise NotImplementedError
