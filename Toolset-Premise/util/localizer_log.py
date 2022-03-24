# -*- coding: utf-8 -*-
"""The logging module which provides different type of messages.
"""
import os
import sys
import inspect
from time import gmtime, strftime
import configparser


__config = configparser.RawConfigParser()
__config.optionxform = str
if os.path.isfile('config.ini'):
    __config.read('config.ini')

__TAGS = {'info': 'INFO',
          'debug': 'DEBUG',
          'error': 'ERROR',
          'warning': 'WARNING'}

# TODO: make it thread safe
__log_files = []


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
        time_section = strftime("%H:%M:%S", gmtime())

        line = "[{timestamp} {tag}][Function:{fun}]{msg}"\
            .format(timestamp=time_section,
                    tag=tag_str,
                    fun=caller,
                    msg=s)
        print(line)

        for log_file in __log_files:
            with open(log_file, 'a') as f:
                f.write(line + '\n')


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
