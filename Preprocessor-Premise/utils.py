import csv
import json
import logging
import os
from datetime import datetime
from typing import Dict
import numpy as np
from ruamel.yaml import YAML
from datetime import timezone


def parse_yaml(file_path) -> Dict:
    """
    Parse a YAML file and load into a Python dictionary.

    :param str file_path: The file path of the YAML file.
    :return: The Python dictionary.
    :rtype: Dict
    """
    yaml = YAML()
    with open(file_path, mode='r') as file:
        result = yaml.load(file)
    return result


# convert datetime object to timestamp in UTC
# DateTime -> Timestamp
def datetime_timestamp_utc(dt_object):
    timestamp = int(dt_object.replace(tzinfo=timezone.utc).timestamp())
    return timestamp


# convert timestamp to datetime in UTC
# Timestamp -> DateTime
def timestamp_to_datetime_utc(timestamp):
    dt_object = datetime.utcfromtimestamp(timestamp)
    return dt_object