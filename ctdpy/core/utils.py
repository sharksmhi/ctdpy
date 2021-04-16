# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 14:46:21 2018

@author: a002028
"""
import os
import numpy as np
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
from collections import Mapping
from fnmatch import fnmatch
from datetime import datetime
import shutil
from trollsift.parser import globify, parse
import inspect
from threading import Thread


def check_path(path):
    """
    :param path:
    :return:
    """
    if not os.path.exists(path):
        os.makedirs(path)


def convert_string_to_datetime_obj(x, fmt):
    """
    :param x: str (can be any kind of date/time related string format)
    :param fmt: format of output
    :return: datetime object
    """
    if type(x) == str:
        return datetime.strptime(x, fmt)
    else:
        return ''


def copyfile(src, dst):
    """
    :param src: Source path
    :param dst: Destination path
    :return: File copied
    """
    thread_process(shutil.copy2, src, dst)
    # shutil.copy2(src, dst)


def copytree(src, dst, symlinks=False, ignore=None, file_paths=None):
    """
    :param src:
    :param dst:
    :param symlinks:
    :param ignore:
    :return:
    """
    items = file_paths or (os.path.join(src, item) for item in os.listdir(src))

    for item in items:
        d = os.path.join(dst, os.path.basename(item))
        if '.' not in item[-5:-2]:
            # so, rather then using os.path.isdir(s) we do a string check to conclude if its a directory or a file that
            # we´re trying to copy. Why?! Because if "s" is a directory on a SLOooW file server, e.g. \\WINFS\prod\
            # os.path.isdir or os.path.isfile will be unnecessary time consuming..
            # assuming that all file extension are between 2 and 4 characters long (eg. '.7z', '.txt', '.xlsx')
            thread_process(shutil.copytree, item, d, symlinks, ignore)
        else:
            thread_process(shutil.copy2, item, d)


def create_directory_structure(dictionary, base_path):
    """
    Creates directory based on nested dictionary
    :param dictionary: nested dictionary
    :param base_path: Base folder
    :return: Folders from keys in dictionary
    """
    if len(dictionary) and not isinstance(dictionary, str):
        for direc in dictionary:
            if isinstance(direc, str):
                if '.' not in direc:
                    create_directory_structure(dictionary[direc], os.path.join(base_path, direc))
            elif isinstance(direc, dict):
                create_directory_structure(dictionary[direc], os.path.join(base_path, direc))
    else:
        os.makedirs(base_path)


def decdeg_to_decmin(pos, string_type=True, decimals=2):
    """
    :param pos: Position in format DD.dddd (Decimal degrees)
    :param string_type: As str?
    :param decimals: Number of decimals
    :return: Position in format DDMM.mm(Degrees + decimal minutes)
    """
    pos = float(pos)
    deg = np.floor(pos)
    minute = pos % deg * 60.0
    if string_type:
        if decimals:
            # FIXME Does not work properly
            output = ('%%2.%sf'.zfill(8) % decimals % (float(deg) * 100.0 + minute))
        else:
            output = (str(deg * 100.0 + minute))
    else:
        output = (deg * 100.0 + minute)
    return output


def decmin_to_decdeg(pos, string_type=True, decimals=4):
    """
    :param pos: str, Position in format DDMM.mm (Degrees + decimal minutes)
    :param string_type: As str?
    :param decimals: Number of decimals
    :return: Position in format DD.dddd (Decimal degrees)
    """
    # pos = pos.replace(' ','')
    # if len(pos.split('.')[0]) > 2:
    #     return pos
    pos = float(pos)
    if pos < 99:
        # Allready in decdeg
        return pos

    output = np.floor(pos/100.) + (pos % 100)/60.
    output = "%.5f" % output
    if string_type:
        return output
    else:
        return float(output)


def eliminate_empty_rows(df):
    return df.loc[df.apply(any, axis=1), :].reset_index(drop=True)


def generate_filepaths(directory, pattern='', not_pattern='DUMMY_PATTERN',
                       pattern_list=None, not_pattern_list=None, endswith='', only_from_dir=True):
    """
    :param directory:
    :param pattern:
    :param not_pattern:
    :param pattern_list:
    :param endswith:
    :param only_from_dir:
    :return:
    """
    pattern_list = pattern_list or []
    not_pattern_list = not_pattern_list or []
    directory = str(directory) # MW: To also allow directory to be of type pathlib.Path
    for path, subdir, fids in os.walk(directory):
        if only_from_dir:
            if path != directory:
                continue
        for f in fids:
            if pattern in f and not_pattern not in f and f.endswith(endswith):
                if any(pattern_list):
                    for pat in pattern_list:
                        if pat in f:
                            yield os.path.abspath(os.path.join(path, f))
                elif any(not_pattern_list):
                    include = True
                    for pat in not_pattern_list:
                        if pat in f:
                            include = False
                    if include:
                        yield os.path.abspath(os.path.join(path, f))
                else:
                    yield os.path.abspath(os.path.join(path, f))


def generate_strings_based_on_suffix(dictionary, suffix):
    """
    :param dictionary: Nested dictionary
    :param suffix: str, e.g. '.txt'
    :return: generator to produce a stringlist
    """
    for item in dictionary.values():
        if isinstance(item, dict):
            yield from generate_strings_based_on_suffix(item, suffix)
        elif not is_sequence(item):
            continue
        else:
            for value in item:
                if value.endswith(suffix):
                    yield value


def get_datetime(date_string, time_string):
    """
    :param date_string: YYYY-MM-DD
    :param time_string: HH:MM:SS  /  HH:MM
    :return:
    """
    if ' ' in date_string:
        date_string = date_string.split(' ')[0]
    if len(time_string) == 8:
        return datetime.strptime(date_string + ' ' + time_string, '%Y-%m-%d %H:%M:%S')
    elif len(time_string) == 5:
        return datetime.strptime(date_string + ' ' + time_string, '%Y-%m-%d %H:%M')
    else:
        return None


def get_datetime_now(fmt='%Y-%m-%d %H:%M:%S'):
    """
    :param fmt:
    :return:
    """
    return datetime.now().strftime(fmt)


def get_file_list_based_on_suffix(file_list, suffix):
    """
    Get filenames endinge with "suffix"
    :param file_list:
    :param suffix:
    :return:
    """
    match_list = []

    for fid in file_list:
        fid = str(fid)  # MW: To also allow fid to be of type pathlib.Path
        if '~$' in fid:
            # memory prefix when a file is open
            continue
        elif fid.endswith(suffix):
            match_list.append(fid)

    return match_list


def get_file_list_match(file_list, match_string): 
    """
    Get filenames containing "match_string"
    :param file_list:
    :param match_string:
    :return:
    """
    match_list = []
    
    for fid in file_list:
        fid = str(fid)  # MW: To also allow fid to be of type pathlib.Path
        if fnmatch(fid, match_string):
            match_list.append(fid)
            
    return match_list


def get_filebase(path, pattern):
    """
    Get the end of *path* of same length as *pattern*
    :param path: str
    :param pattern: str
    :return:
    """
    # A pattern can include directories
    tail_len = len(pattern.split(os.path.sep))
    return os.path.join(*path.split(os.path.sep)[-tail_len:])


def get_filename(file_path):
    """
    :param file_path:
    :return:
    """
    return os.path.basename(file_path)


def get_format_from_datetime_obj(x, fmt):
    """
    :param x: datetime object
    :param fmt: format of output
    :return: str (can be any kind of date/time related string format)
    """
    try:
        return x.strftime(fmt)
    except:
        return ''


def get_index_where_df_equals_x(df, x):
    """
    :param df: pd.DataFrame
    :param x: any kind of value
    :return: Boolean
    """
    return np.where(df == x)


def get_kwargs(func, info):
    """
    Creates a key word dictionary to use as input to "func"
    :param func: Function
    :param info: Dictionary with info to include in kwargs
    :return: kwargs
    """
    funcargs = inspect.getfullargspec(func)
    kwargs = {key: info.get(key) for key in funcargs.args}
    return kwargs


def get_method_dictionary(obj):
    """
    :param obj: Object
    :return: Dictionary of all methods from object including those from parent classes
    """
    return {func: True for func in dir(obj) if not func.startswith("__")}


def get_object_path(obj):
    """
    :param obj:
    :return:
    """
    return obj.__module__ + "." + obj.__name__


def get_reversed_dictionary(dictionary, keys):
    """
    :param dictionary:
    :param keys:
    :return:
    """
    return {dictionary.get(k): k for k in keys if dictionary.get(k)}


def get_timestamp(x):
    """
    :param x:
    :return:
    """
    return pd.Timestamp(x)


def get_time_as_format(**kwargs):
    if kwargs.get('now'):
        d = datetime.now()
    elif kwargs.get('timestamp'):
        raise NotImplementedError

    if kwargs.get('fmt'):
        return d.strftime(kwargs.get('fmt'))
    else:
        raise NotImplementedError


def get_timestamp_minus_daydelta(date, delta=1):
    """
    :param date:
    :param delta:
    :return:
    """
    return date - pd.DateOffset(delta)


def match_filenames(filenames, pattern):
    """
    Get the filenames matching *pattern*
    :param filenames: list
    :param pattern: str
    :return:
    """
    matching = []
    for filename in filenames:
        filename = str(filename) # MW: To also allow filename to be of type pathlib.Path
        if '~$' in filename:
            # memory prefix when a file is open
            continue
        if type(pattern) == list:
            for p in pattern:
                if fnmatch(get_filebase(filename, p), globify(p)):
                    matching.append(filename)
        else:
            if fnmatch(get_filebase(filename, pattern), globify(pattern)):
                matching.append(filename)
    return matching


def is_sequence(arg):
    """
    Checks if an object is iterable (you can loop over it) and not a string
    ** Taken from SHARKToolbox
    :param arg:
    :return:
    """
    return (not hasattr(arg, "strip") and
            hasattr(arg, "__iter__"))


def recursive_dict_update(d, u):
    """ Recursive dictionary update using
    Copied from:
        http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
        via satpy
    """
    for k, v in u.items():
        if isinstance(v, Mapping):
            r = recursive_dict_update(d.get(k, {}), v)
            d.setdefault(k, r)
        else:
            d.setdefault(k, u[k])
    return d
    #         d[k] = r
    #     else:
    #         d[k] = u[k]
    # return d


def round_value(value, nr_decimals=3):
    """ Calculate rounded value
        2019-02-11
        2019-03-11: Updated with ROUND_HALF_UP
    """
    return str(Decimal(str(value)).quantize(Decimal('%%1.%sf' %nr_decimals % 1),
                       rounding=ROUND_HALF_UP))


def f_string_1(value):
    return f'{value:.1f}'


def f_string_2(value):
    return f'{value:.2f}'


def f_string_3(value):
    return f'{value:.3f}'


def f_string_4(value):
    return f'{value:.4f}'


def rounder(values, decimals=3):
    if decimals == 3:
        return np.vectorize(f_string_3)(values)
    elif decimals == 2:
        return np.vectorize(f_string_2)(values)
    elif decimals == 1:
        return np.vectorize(f_string_1)(values)
    elif decimals == 4:
        return np.vectorize(f_string_4)(values)
    else:
        return values


def set_export_path(export_dir=None):
    """
    :param export_dir:
    :return:
    """
    export_dir = export_dir or os.getcwd() + '/exports'

    if not os.path.isdir(export_dir):
        os.makedirs(export_dir)


def strip_text(x, text, strip=True):
    """
    :param x:
    :param text:
    :return:
    """
    new_x = x
    if type(x) == str:
        if not type(text) == list:
            text = [text]
        for t in text:
            new_x = new_x.replace(t, '')
        if strip:
            new_x = new_x.strip()
    else:
        new_x = ''
    return new_x


def thread_process(call_function, *args, **kwargs):
    """
    :param call_function:
    :param args:
    :param kwargs:
    :return:
    """
    Thread(target=call_function, args=args, kwargs=kwargs).start()
