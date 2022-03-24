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

kpi_list_file_path = "resources/data/0-meta/kpi-list.csv"

anomalies_file_path = "resources/data/3-novelties-in-csv/n8a_1__n8a_04.txt.csv"
premise_exp_folder_path = "resources/data/15-premise-data/anomalies-2/test-data/9999999998-10.40.7.172-failurefree_x_x"

# anomalies_file_path = "resources/data/3-novelties-in-csv/n8a_1__n8b_04.txt.csv"
# premise_exp_folder_path = "resources/data/15-premise-data/anomalies-2/test-data/9999999999-10.40.7.172-failurefree_x_x"

premise_exp_file_name_pattern = "{minute_of_experiment}.txt"
premise_exp_file_row_pattern = "('{pair_id}', 'x', '{metric}')\n"

# ******************************************************************************************* fUNCTIONS


def get_kpi_list(_kpi_list_file_path):
    _fil = open(_kpi_list_file_path, 'r')
    _reader = csv.reader(_fil)
    _header = next(_reader, None)

    return _header


def get_pair_id_by_node_name(node_name, cluster_node_pairs):

    result_node_pair_id = -1

    for node_pair_id in range(len(cluster_node_pairs)):
        if node_name in cluster_node_pairs[node_pair_id]:
            result_node_pair_id = node_pair_id

    if result_node_pair_id == -1:
        print("Node ", node_name, " does not exist in the KPI List")
        exit(1)

    return result_node_pair_id


def create_folder(folder_path):
    if not os.path.exists(folder_path):
        try:
            os.mkdir(folder_path)
        except OSError:
            print("Creation of the directory %s failed" % folder_path)
            exit(1)


def gen_exp_unique_code(p_exp_unique_code):
    unique_code_str = ""

    for zz in range(10 - len(str(p_exp_unique_code))):
        unique_code_str += "0"

    return unique_code_str + str(p_exp_unique_code)


# ******************************************************************************************* RUN

kpi_list = get_kpi_list(os.path.join(script_dir, kpi_list_file_path))

cluster_node_pairs = str(configuration['nodes']['pairs']).split(", ")
for ii in range(len(cluster_node_pairs)):
    cluster_node_pairs[ii] = cluster_node_pairs[ii].split(" ")

create_folder(premise_exp_folder_path)

f = open(anomalies_file_path, 'r')
reader = csv.reader(f)
header = next(reader, None)

ii = 0
# Loop by rows in the experiment file
for row in reader:
    premise_exp_file_path = os.path.join(premise_exp_folder_path, premise_exp_file_name_pattern.format(minute_of_experiment=(ii + 1)))

    for kpi_index in range(len(kpi_list)):
        cell_value = int(row[kpi_index + 1])
        if cell_value == 1:
            kpi = str(kpi_list[kpi_index])
            node_name = kpi.split("_")[0]
            node_pair_id = get_pair_id_by_node_name(node_name, cluster_node_pairs)
            record = premise_exp_file_row_pattern.format(pair_id=node_pair_id, metric=kpi)
            with open(premise_exp_file_path, "a") as file_object:
                file_object.write(record)

    ii += 1
