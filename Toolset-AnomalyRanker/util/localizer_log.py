# -*- coding: utf-8 -*-
"""The logging module which provides different type of messages.
"""
import os
import re
import sys
import gzip
import shutil
import inspect
from time import gmtime, strftime
import configparser


__config = configparser.RawConfigParser()
__config.optionxform = str
if os.path.isfile('config'):
    __config.read('config')

__TAGS = {'info': 'INFO',
          'debug': 'DEBUG',
          'error': 'ERROR',
          'warning': 'WARNING'}

# TODO: make it thread safe
__log_files = []
__logsize = None
__backups = None


def msg(s):
    """Print a debug message.

    It will only print when '[default]/<debug>' in the config file is set to
    true.

    Args:
        s(str): The string to print.

    Returns:
        None
    """
    global __config
    if __config.getboolean('default', 'debug'):
        output(s, 'debug')


def error(s):
    """Print a error message and quit with code -1.

    Args:
        s(str): The string to print.

    Returns:
        None
    """
    output(s, 'error')
    sys.exit(-1)


def warning(s):
    """Print a warning message and quit with code -1.

    Args:
        s(str): The string to print.

    Returns:
        None
    """
    output(s, 'warning')


def stdout(s):
    """Print a info message.

    Args:
        s(str): The string to print.

    Returns:
        None
    """
    output(s, 'info')


def output(s, tag):
    """Print funciton used by diffent type of print functions.

    Args:
        s(str): The string to print.
        tag(str): The type of prefix of the message.

    Returns:
        None
    """
    global __log_files
    global __TAGS
    if tag in __TAGS:
        tag_str = __TAGS[tag]

        caller = inspect.stack()[2][3]
        time_section = strftime("%Y-%m-%d %H:%M:%S", gmtime())

        line = "[{timestamp} {tag}][Function:{fun}]{msg}"\
            .format(timestamp=time_section,
                    tag=tag_str,
                    fun=caller,
                    msg=s)
        print(line)

        for log_file in __log_files:
            write_log(log_file, line + '\n')


def write_log(logfile_path, content):
    """Write a line to a config file.

    If file exceeds limit, backup the file and write to a new file. The maximun
    file size and maximum number of backups are defined under
    '[restful]/<logfile_size>' and '[restful]/<logfile_backups>'. See README
    for more information.

    Args:
        logfile_path(str): The path of the logfile.
        content(str): The content to write

    Returns:
        None
    """
    global __backups
    DEFAULT_BACKUPS = 10
    if not __backups:
        if __config.has_section('restful') and \
                __config.has_option('restful', 'logfile_backups'):
            backups_str = __config.get('restful', 'logfile_backups')
            try:
                __backups = int(backups_str)
            except ValueError:
                print(('Logfile number of backups option cannot be parsed. '
                       'Use defulat {backups}')
                      .format(backups=DEFAULT_BACKUPS))
                __backups = DEFAULT_BACKUPS
        else:
            print(('Logfile number of backups option not found. '
                   'use defulat {backups}')
                  .format(backups=DEFAULT_BACKUPS))
            __backups = DEFAULT_BACKUPS

    # Chck if needed to create new file
    if check_size(logfile_path):
        path_tuple = os.path.split(logfile_path)
        logfile_dir = path_tuple[:-1]
        logfile_name = path_tuple[-1]
        print(list(logfile_dir))

        bk_list = [os.path.join(*logfile_dir,
                                '.'.join([logfile_name, str(i+1), 'gz']))
                   for i in reversed(range(__backups))]

        # backup old gz files
        for i in range(0, len(bk_list)-1):
            if os.path.exists(bk_list[i+1]):
                os.rename(bk_list[i+1], bk_list[i])

        # Create gzip of current log file if exists
        if len(bk_list) > 0 and os.path.exists(logfile_path):
            with open(logfile_path, 'rb') as f_in:
                with gzip.open(bk_list[-1], 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(logfile_path)

    with open(logfile_path, 'a') as f:
        f.write(content)


def check_size(logfile_path):
    """Check if the size of the file exceeds limit.

    The maximun file size is defined under '[restful]/<logfile_size>'. See
    README for more information.

    Args:
        logfile_path(str): The path of the logfile.

    Returns:
        True if the file size excceds the limit. Otherwise false.
    """
    if not os.path.isfile(logfile_path):
        return False

    DEFAULT_SIZE = '10M'

    # convert string to size in bytes, if cannot be parsed, return None
    def size_in_bytes(size):
        UNITS = [('', 'B'),
                 ('K', 'KB'),
                 ('M', 'MB'),
                 ('G', 'GB'),
                 ('T', 'TB'),
                 ('P', 'PB'),
                 ('E', 'EB'),
                 ('Z', 'ZB'),
                 ('Y', 'YB')]
        # Split the size option to ('', ${number}, ${unit})
        size_terms = re.split('(\d+)', size)
        size_in_bytes = None
        if len(size_terms) == 3:
            start, number, unit = size_terms
            if any(map(lambda x: unit in x, UNITS)):
                unit_power = next((i for i, v in enumerate(UNITS)
                                   if unit in v))
                try:
                    number = int(number)
                    size_in_bytes = 1024 ** unit_power * number
                except ValueError:
                    pass

        return size_in_bytes

    DEFAULT_SIZE_IN_BYTES = size_in_bytes(DEFAULT_SIZE)

    global __config
    global __logsize

    if not __logsize:
        if __config.has_section('restful') and \
                __config.has_option('restful', 'logfile_size'):
            size = __config.get('restful', 'logfile_size')
        else:
            print('Logfile size option not found. use defulat size {size}'
                  .format(size=DEFAULT_SIZE))
            size = DEFAULT_SIZE

        __logsize = size_in_bytes(size)
        if not __logsize:
            print(('Logfile size option cannot be parsed. '
                   'use defulat size {size}')
                  .format(size=DEFAULT_SIZE))
            __logsize = DEFAULT_SIZE_IN_BYTES

    return os.path.getsize(logfile_path) > __logsize


def reg_file(f_name):
    """Register a file name as the log file to write.

    Args:
        f_name(str): The name of the log file.

    Returns:
        None
    """
    global __log_files
    dir_, file_ = os.path.split(f_name)
    if dir_ and not os.path.exists(dir_):
        os.makedirs(dir_, exist_ok=True)
    if file_:
        __log_files.append(f_name)
