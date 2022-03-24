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


# ***

# kpi => recourse
def get_recourse_from_kpi(kpi_):
    kpi_components_list_ = kpi_.split("_")
    recourse_ = kpi_components_list_[0]

    return recourse_


# kpi => metric
def get_metric_from_kpi(kpi_):
    kpi_components_list_ = kpi_.split("_")
    metric_ = "_".join(kpi_components_list_[1:])

    return metric_


# kpi, new_recourse -> new_kpi
def change_recourse_in_kpi(kpi_, new_recourse_):
    metric_ = get_metric_from_kpi(kpi_)
    new_kpi_ = new_recourse_ + "_" + metric_

    return new_kpi_


# ******************************************************************************************* Configuration

script_dir = os.path.dirname(os.path.abspath(__file__))

configuration_file_path = os.path.join(script_dir, 'resources/configuration/configuration.yml')
configuration: Dict = utils.parse_yaml(configuration_file_path)

data_sets_configuration_file_path = os.path.join(script_dir, 'resources/configuration/data_sets.yml')
data_sets_configuration: Dict = utils.parse_yaml(data_sets_configuration_file_path)

input_files_dir = "resources/data/2-anomalies-in-csv/"
output_files_dir = "resources/data/4-anomalies-in-csv-shuffled/"

# ******************************************************************************************* Inputs

anomalies_file_name = str(sys.argv[1])
experiment_data_set_code = str(sys.argv[2])

# ****************************************************************************************** Data set Configuration

cluster_node_pairs = str(configuration['nodes']['pairs']).split(", ")
for ii in range(len(cluster_node_pairs)):
    cluster_node_pairs[ii] = cluster_node_pairs[ii].split(" ")

faulty_node_0 = cluster_node_pairs[0][0]
faulty_node_1 = cluster_node_pairs[0][1]

# ******************************************************************************************* Local Configuration

anomalies_file_path_csv = os.path.join(script_dir, input_files_dir + anomalies_file_name)

for jj in range(0, len(cluster_node_pairs)):

    anomalies_file_path_csv_shuffled = os.path.join(script_dir,
                                                    output_files_dir + str(experiment_data_set_code) + "-" + str(jj) + ".csv")

    if jj == 0:
        copyfile(anomalies_file_path_csv, anomalies_file_path_csv_shuffled)
        continue

    target_node_0 = cluster_node_pairs[jj][0]
    target_node_1 = cluster_node_pairs[jj][1]

    f = open(anomalies_file_path_csv, 'r')
    reader = csv.reader(f)
    header = next(reader, None)

    header_original = []
    for item in header:
        header_original.append(item)

    print(jj, anomalies_file_path_csv_shuffled)
    with open(anomalies_file_path_csv_shuffled, 'w') as outfile:
        writer = csv.writer(outfile)

        for zz in range(len(header_original)):

            kpi = header_original[zz]
            recourse = get_recourse_from_kpi(kpi)

            if recourse == target_node_0:
                kpi = change_recourse_in_kpi(kpi, faulty_node_0)
                pass

            if recourse == target_node_1:
                kpi = change_recourse_in_kpi(kpi, faulty_node_1)
                pass

            if recourse == faulty_node_0:
                kpi = change_recourse_in_kpi(kpi, target_node_0)
                pass

            if recourse == faulty_node_1:
                kpi = change_recourse_in_kpi(kpi, target_node_1)
                pass

            header[zz] = kpi

        writer.writerow(header)
        for row in reader:
            writer.writerow(row)

    f = open(anomalies_file_path_csv_shuffled, 'r')
    reader = csv.reader(f)

    matrix = []
    ff = 0
    for row in reader:
        if ff > 0:
            matrix.append(row)
        else:
            the_header = row
        ff += 1

    pdf = pd.DataFrame(matrix)
    pdf.columns = the_header
    # print(pdf.head())

    pdf_new = pd.DataFrame()
    for kpi in header_original:
        pdf_new[kpi] = pdf[kpi]
    # print(pdf_new.head())

    pdf_new.to_csv(anomalies_file_path_csv_shuffled, index=False)
