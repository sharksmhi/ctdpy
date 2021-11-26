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
from trollsift.parser import globify
import inspect
from threading import Thread


def check_path(path):
    """Create fodler if path doesn´t exists."""
    if not os.path.exists(path):
        os.makedirs(path)


def convert_string_to_datetime_obj(x, fmt):
    """Get datetime object from string."""
    if type(x) == str:
        return datetime.strptime(x, fmt)
    else:
        return ''


def copyfile(src, dst):
    """Copy file in thread."""
    thread_process(shutil.copy2, src, dst)


def copytree(src, dst, symlinks=False, ignore=None, file_paths=None):
    """Copy folder tree."""
    items = file_paths or (os.path.join(src, item) for item in os.listdir(src))

    for item in items:
        d = os.path.join(dst, os.path.basename(item))
        if '.' not in item[-5:-2]:
            # so, rather then using os.path.isdir(s) we do a string check to conclude if its a directory or a file that
            # we´re trying to copy. Why?! Because item might be a directory on a SLOooW file server..
            # os.path.isdir or os.path.isfile will be unnecessary time consuming..
            # assuming that all file extension are between 2 and 4 characters long (eg. '.7z', '.txt', '.xlsx')
            thread_process(shutil.copytree, item, d, symlinks, ignore)
        else:
            thread_process(shutil.copy2, item, d)


def create_directory_structure(dictionary, base_path):
    """Create directory based on nested dictionary."""
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
    """Convert position from decimal degrees into degrees and decimal minutes."""
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
    """Convert position from degrees and decimal minutes into decimal degrees."""
    pos = float(pos)
    if pos < 99:
        # Allready in decdeg
        return pos

    output = np.floor(pos / 100.) + (pos % 100) / 60.
    output = "%.5f" % output
    if string_type:
        return output
    else:
        return float(output)


def eliminate_empty_rows(df):
    """Return dataframe without empty rows."""
    return df.loc[df.apply(any, axis=1), :].reset_index(drop=True)


def generate_filepaths(directory, pattern='', not_pattern='DUMMY_PATTERN',
                       pattern_list=None, not_pattern_list=None, endswith='', only_from_dir=True):
    """Generate file paths."""
    pattern_list = pattern_list or []
    not_pattern_list = not_pattern_list or []
    directory = str(directory)  # MW: To also allow directory to be of type pathlib.Path
    for path, _, fids in os.walk(directory):
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
    """Generate stringlist.

    Args:
        dictionary: Nested dictionary
        suffix (str): '.txt' or '.cnv'
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
    """Get datetime object based on both date and time.

    Args:
        date_string: YYYY-MM-DD
        time_string: HH:MM:SS  /  HH:MM
    """
    # TODO this is not that pretty..
    if ' ' in date_string:
        date_string = date_string.split(' ')[0]
    if len(time_string) == 8:
        return datetime.strptime(date_string + ' ' + time_string, '%Y-%m-%d %H:%M:%S')
    elif len(time_string) == 5:
        return datetime.strptime(date_string + ' ' + time_string, '%Y-%m-%d %H:%M')
    else:
        return None


def get_datetime_now(fmt='%Y-%m-%d %H:%M:%S'):
    """Get datetime object according to the given format for time right NOW."""
    return datetime.now().strftime(fmt)


def get_file_list_based_on_suffix(file_list, suffix):
    """Get filenames ending with the given suffix."""
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
    """Get filenames containing the given match_string."""
    match_list = []

    for fid in file_list:
        fid = str(fid)  # MW: To also allow fid to be of type pathlib.Path
        if fnmatch(fid, match_string):
            match_list.append(fid)

    return match_list


def get_filebase(path, pattern):
    """Get the end of *path* of same length as *pattern*."""
    # A pattern can include directories
    tail_len = len(pattern.split(os.path.sep))
    return os.path.join(*path.split(os.path.sep)[-tail_len:])


def get_filename(file_path):
    """Get filename from filepath."""
    return os.path.basename(file_path)


def get_filename_without_extension(file_path):
    """Get filename without extension from filepath."""
    return os.path.basename(file_path).split('.')[0]


def get_format_from_datetime_obj(x, fmt):
    """Return str from datetime object according to the given format."""
    try:
        return x.strftime(fmt)
    except Exception:
        return ''


def get_index_where_df_equals_x(df, x):
    """Return boolean array."""
    return np.where(df == x)


def get_kwargs(func, info):
    """Return a key word dictionary to use as input to "func".

    Args:
        func: Function
        info: Dictionary with info to include in kwargs
    """
    funcargs = inspect.getfullargspec(func)
    kwargs = {key: info.get(key) for key in funcargs.args}
    return kwargs


def get_method_dictionary(obj):
    """Return dictionary of all methods from the given object, including those from parent classes."""
    return {func: True for func in dir(obj) if not func.startswith("__")}


def get_object_path(obj):
    """Return path to object."""
    return obj.__module__ + "." + obj.__name__


def get_reversed_dictionary(dictionary, keys):
    """Return reveresed dictionary."""
    return {dictionary.get(k): k for k in keys if dictionary.get(k)}


def get_timestamp(x):
    """Get pandas Timestamp from x."""
    return pd.Timestamp(x)


def get_time_as_format(**kwargs):
    """Get time as format in kwargs."""
    if kwargs.get('now'):
        d = datetime.now()
    elif kwargs.get('timestamp'):
        raise NotImplementedError

    if kwargs.get('fmt'):
        return d.strftime(kwargs.get('fmt'))
    else:
        raise NotImplementedError


def get_timestamp_minus_daydelta(date, delta=1):
    """Get timestamp based on date and delta."""
    return date - pd.DateOffset(delta)


def match_filenames(filenames, pattern):
    """Get the filenames matching *pattern*."""
    matching = []
    for filename in filenames:
        filename = str(filename)  # MW: To also allow filename to be of type pathlib.Path
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


def milliseconds(ts):
    """Get milliseconds."""
    return ts.strftime('%S.%f')[:-3]


def is_sequence(arg):
    """Return if an object is iterable (you can loop over it) and not a string."""
    return (not hasattr(arg, "strip") and hasattr(arg, "__iter__"))


def recursive_dict_update(d, u):
    """Recursive dictionary update.

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


def round_value(value, nr_decimals=3):
    """Calculate rounded value."""
    return str(Decimal(str(value)).quantize(Decimal('%%1.%sf' % nr_decimals % 1),
                                            rounding=ROUND_HALF_UP))


def f_string_1(value):
    """Round value with 1 decimals."""
    return f'{value:.1f}'


def f_string_2(value):
    """Round value with 2 decimals."""
    return f'{value:.2f}'


def f_string_3(value):
    """Round value with 3 decimals."""
    return f'{value:.3f}'


def f_string_4(value):
    """Round value with 4 decimals."""
    return f'{value:.4f}'


def rounder(values, decimals=3):
    """Round the given values with number of decimals."""
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
    """Create export folder."""
    export_dir = export_dir or os.getcwd() + '/exports'

    if not os.path.isdir(export_dir):
        os.makedirs(export_dir)


def strip_text(x, text, strip=True):
    """Return a stripped string."""
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
    """Thread process.

    Args:
        call_function: function to use
        args: Arguments to call_function
        kwargs: Key word arguments to call_function
    """
    Thread(target=call_function, args=args, kwargs=kwargs).start()
