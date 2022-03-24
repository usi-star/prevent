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

# ******************************************************************************************* PARAMETERS

data_sets_normal_dir = "resources/data/3-novelties-in-csv/"
data_sets_normal_filename = "n8a_1__n8b_04.csv"

novelty_file_path = "resources/data/3-novelties-in-csv/n8a_1__n8b_04.csv"
experiment_files_dir = "resources/data/4-anomalies-in-csv-shuffled/"
training_sets_dir = "resources/data/5-training-sets/"

number_of_pairs = 10
faults_set_1 = [1, 2, 3, 4, 6]
faults_set_2 = [7, 8, 9, 10]

training_sets_filename_prefix = "training-set-"

# ******************************************************************************************* Inputs

model = str(sys.argv[1])

# ******************************************************************************************* fUNCTIONS


def import_csv_content(source_data_set_file_path, nodes_pair_number, number_of_features, writer, include_header=False):

    f = open(source_data_set_file_path, 'r')
    reader = csv.reader(f)
    header = next(reader, None)

    del header[0]

    if include_header:
        writer.writerow(header)

    for row in reader:
        del row[0]

        class_column_index = number_of_features
        class_current = row[class_column_index]
        if class_current != "n":
            class_new = str(class_current) + "-" + str(nodes_pair_number)
            row[class_column_index] = class_new

        writer.writerow(row)


def get_number_of_features(source_data_set_file_path):
    f = open(source_data_set_file_path, 'r')
    reader = csv.reader(f)
    header = next(reader, None)

    return len(header) - 2


def generate_file_path(script_dir, experiment_files_dir, experiment_data_set_code, pair_number):
    return os.path.join(script_dir, experiment_files_dir + experiment_data_set_code + "-" + str(pair_number) + ".csv")


# ******************************************************************************************* RUN

if model == "1":
    fault_set = faults_set_1
    fake_fault_set = faults_set_2
else:
    fault_set = faults_set_2
    fake_fault_set = faults_set_1

novelty_file_path = os.path.join(script_dir, data_sets_normal_dir + data_sets_normal_filename)
number_of_features = get_number_of_features(novelty_file_path)

training_set_filename = training_sets_filename_prefix + '_'.join([str(elem) for elem in fault_set]) + ".csv"
training_set_file_path = os.path.join(script_dir, training_sets_dir + training_set_filename)

with open(training_set_file_path, 'w') as outfile:
    writer = csv.writer(outfile)

    # import the content of the normal data set
    import_csv_content(novelty_file_path, "", number_of_features, writer, True)

    for ii in range(len(fault_set)):
        experiment_data_set_code = "e" + str(fault_set[ii])
        for pair_number in range(number_of_pairs):
            # import the content of the test data set
            import_csv_content(generate_file_path(script_dir, experiment_files_dir, experiment_data_set_code, pair_number), pair_number, number_of_features, writer, False)

    # add complementary fake labels
    for fault_type in fake_fault_set:
        writer.writerow(["1" for i in range(number_of_features)] + ["e" + str(fault_type) + "-0"])
