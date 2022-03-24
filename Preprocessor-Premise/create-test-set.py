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

# ******************************************************************************************* Configuration

script_dir = os.path.dirname(os.path.abspath(__file__))

configuration_file_path = os.path.join(script_dir, 'resources/configuration/configuration.yml')
configuration: Dict = utils.parse_yaml(configuration_file_path)

data_sets_configuration_file_path = os.path.join(script_dir, 'resources/configuration/data_sets.yml')
data_sets_configuration: Dict = utils.parse_yaml(data_sets_configuration_file_path)

# ******************************************************************************************* Parameters

nodes_pair_number = 0

fault_code_prefix = "e"
fault_ids_list = [1, 2, 3, 4, 6, 7, 8, 9, 10]

novelty_file_path = "resources/data/3-novelties-in-csv/n8a_1__n8b_04.csv"
anomaly_set_file_path_pattern = "resources/data/4-anomalies-in-csv-shuffled/{fault_code}-{nodes_pair_number}.csv"
test_set_file_path_pattern = "resources/data/6-test-sets/test-set-{fault_code}.csv"

# ******************************************************************************************* Functions


def get_header_normal(script_dir, novelty_file_path):
    data_set_normal_file = os.path.join(script_dir, novelty_file_path)
    f = open(data_set_normal_file, 'r')
    reader = csv.reader(f)
    header_training_set = next(reader, None)

    return header_training_set


# ******************************************************************************************* RUN

header_training_set = get_header_normal(script_dir, novelty_file_path)
del header_training_set[0]

for fault_id in fault_ids_list:
    fault_code = fault_code_prefix + str(fault_id)
    test_set_file_path = test_set_file_path_pattern.format(fault_code=fault_code)

    with open(test_set_file_path, 'w') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header_training_set)

        anomaly_set_file_path = anomaly_set_file_path_pattern.format(fault_code=fault_code, nodes_pair_number=nodes_pair_number)
        f = open(anomaly_set_file_path, 'r')
        reader = csv.reader(f)
        header = next(reader, None)

        for row in reader:

            # delete the timestamp column
            del row[0]

            # add the nodes-pair code to the class label
            class_column_index = len(row) - 1
            class_current = row[class_column_index]
            if class_current != "n":
                class_new = str(class_current) + "-" + str(nodes_pair_number)
                row[class_column_index] = class_new

            writer.writerow(row)
