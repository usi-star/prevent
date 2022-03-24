import csv
import os
import sys
import requests
import pandas as pd
from datetime import datetime
import utils
from ruamel.yaml import YAML
from typing import Dict
from shutil import copyfile
from os import path

# ******************************************************************************************* Configuration

script_dir = os.path.dirname(os.path.abspath(__file__))

configuration_file_path = os.path.join(script_dir, 'resources/configuration/configuration.yml')
configuration: Dict = utils.parse_yaml(configuration_file_path)

data_sets_configuration_file_path = os.path.join(script_dir, 'resources/configuration/data_sets.yml')
data_sets_configuration: Dict = utils.parse_yaml(data_sets_configuration_file_path)

# ******************************************************************************************* PARAMETERS

scr_kpi_list_file_path = "resources/data/premise-data/meta/kpi-list.csv"
dst_kpi_list_file_path = "resources/data/premise-data/meta/kpi_indices.txt"
record_pattern = "id:{row_id}, resource: {res}, group: x, metric: {metric}\n"

number_of_features = 1720

# ******************************************************************************************* fUNCTIONS


def get_header_normal(_kpi_list_file_path):
    _fil = open(_kpi_list_file_path, 'r')
    _reader = csv.reader(_fil)
    _header = next(_reader, None)

    return _header


def get_pair_id_by_node_name(node_name, cluster_node_pairs):

    result_node_pair_id = -1

    for node_pair_id in range(len(cluster_node_pairs)):
        if node_name in cluster_node_pairs[node_pair_id]:
            result_node_pair_id = node_pair_id

    return result_node_pair_id


# ******************************************************************************************* RUN

cluster_node_pairs = str(configuration['nodes']['pairs']).split(", ")
for ii in range(len(cluster_node_pairs)):
    cluster_node_pairs[ii] = cluster_node_pairs[ii].split(" ")

scr_kpi_list = get_header_normal(os.path.join(script_dir, scr_kpi_list_file_path))

ii = 0
for kpi in scr_kpi_list:

    node_name = kpi.split("_")[0]
    node_pair_id = get_pair_id_by_node_name(node_name, cluster_node_pairs)

    record = record_pattern.format(row_id=ii, res=node_pair_id, metric=kpi)
    with open(dst_kpi_list_file_path, "a") as file_object:
        file_object.write(record)

    ii += 1


