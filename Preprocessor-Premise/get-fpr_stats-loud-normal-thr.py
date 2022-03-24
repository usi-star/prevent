"""
Calculates FPR of LOUD on normal data. The classification is considered as positive if
"""

import plotly.graph_objects as go
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

file_path_raw_localisations = "resources/data/NORMAL/{project_folder}/row-localisations/row-localisations.csv"
file_path_classifications = "resources/data/NORMAL/{project_folder}/{project_name}-predictions-ma-2-outof-3/{exp_code}.csv"
consolidated_file_path_pattern = "resources/data/NORMAL/{project_folder}/{project_name}-consolidated-ma-2-outof-3/{project_name}-classifications-{exp_code}.csv"

experiments = [{"project": "preface", "folder": "13-preface-data",
                "exp_codes": [1, 2, 3, 4, 5, 7, 8, 9, 10]},
               {"project": "embed", "folder": "14-embed-data",
                "exp_codes": [1, 2, 3, 4, 5, 7, 8, 9, 10]},
               {"project": "premise", "folder": "15-premise-data",
                "exp_codes": [1, 2, 3, 4, 5, 7, 8, 9, 10]},
               {"project": "loud-normal", "folder": "17-loud-normal-data",
                "exp_codes": [1, 2, 3, 4, 5, 7, 8, 9, 10]},
               {"project": "loud-normal-thr", "folder": "18-loud-normal-thr-data",
                "exp_codes": [1, 2, 3, 4, 5, 7, 8, 9, 10]}]

colors_by_project = ["rgb(135,206,250)", "rgb(255,189,85)", "rgb(160,160,160)", "rgb(0, 204, 150)", "rgb(135,206,250)"]
dash_sizes_by_localisation_type = [4, 16, 44, 0.5]
marker_line_width = 3
inter_groups_margin = 3
inter_bars_margin = 3
group_size = inter_groups_margin + len(experiments) * inter_bars_margin
projects_set_to_draw = [4]
exp_code = "n8b"


def get_pred(raw_loc_matrix, time_point, period):

    lst = [raw_loc_matrix[time_point - ii] for ii in range(period)]
    intersection = lst[0].intersection(*lst)

    if len(intersection) >= 2:
        return 1
    else:
        return 0


# ******************************************************************************************* RUN

fig = go.Figure()

for project_index, project in enumerate(experiments):
    if project_index not in projects_set_to_draw:
        continue

    project_name = project["project"]
    project_folder = project["folder"]

    # Read Load consolidated file to the matrix
    project_Loud = experiments[3]
    file_path = consolidated_file_path_pattern.format(project_folder=project_Loud["folder"], project_name=project_Loud["project"], exp_code=exp_code)
    f = open(file_path, 'r')
    reader = csv.reader(f)
    header = next(reader, None)
    matrix = []
    for row in reader:
        matrix.append(row)

    # Read localisations matrix - vectors like [0, 1, 0] where [None, Weak, Strong].
    f_name = os.path.join(script_dir, file_path_raw_localisations.format(project_folder=project_folder))
    localisations_file_reader = csv.reader(open(f_name, 'r'))
    raw_localisations_matrix = []
    for row in localisations_file_reader:

        if len(row) >= 3:
            el1 = row[2]
        else:
            el1 = ""

        if len(row) >= 5:
            el2 = row[4]
        else:
            el2 = ""

        if len(row) >= 7:
            el3 = row[6]
        else:
            el3 = ""

        raw_localisations_matrix.append({el1, el2, el3})

    max_period = 21
    min_period = 3

    loud_normal_thr_fps = [0 for ii in range(max_period)]
    FPR = []
    for period in range(min_period, max_period):
        classifications_array = []
        time_point = -1
        for localisation_vector in raw_localisations_matrix:
            time_point += 1
            classification = get_pred(raw_localisations_matrix, time_point, period=period)
            classifications_array.append(classification)

        # Collect localisations to the bar_sections
        for row_index in range(len(matrix) - 1):

            if classifications_array[row_index] == 1:
                localisation_type = 2
                loud_normal_thr_fps[period] += 1
            else:
                localisation_type = 3

        FPR.append(round(loud_normal_thr_fps[period] * 100/10080))

    print(FPR)

