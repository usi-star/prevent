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

localisations_consolidated_file_path = os.path.join(script_dir, "resources/data/NORMAL/localisations_consolidated/localisations_consolidated_normal_6_12.csv")
localisations_raw_file_path = os.path.join(script_dir, "resources/data/NORMAL/localisations_raw/localisations_raw_normal_6_12.csv")
classifications_file_path = os.path.join(script_dir, "resources/data/NORMAL/{project_folder}/{project_name}_predictions_ma_2_3/{project_name}_predictions_ma_2_3_normal_1_14.csv")

experiments = [{"project": "preface-normal",    "folder": "19-preface-normal_data"},
               {"project": "embed-normal",      "folder": "20-embed-normal_data"},
               {"project": "premise-normal",    "folder": ""},
               {"project": "loud-normal",       "folder": "17-loud-normal_data"},
               {"project": "loud-normal-thr",   "folder": "18-loud-normal-thr_data"}]

# Graph parameters
colors_by_project = ["rgb(135,206,250)", "rgb(255,189,85)", "rgb(160,160,160)", "rgb(0, 204, 150)", "rgb(135,206,250)"]
dash_sizes_by_localisation_type = [4, 16, 44, 0.5]
marker_line_width = 3
inter_groups_margin = 3
inter_bars_margin = 3
group_size = inter_groups_margin + len(experiments) * inter_bars_margin

# Run parameters
projects_set_to_draw = [0, 1, 3, 4]
TOTAL_DURATION = 10080

# ******************************************************************************************* FUNCTIONS


def get_ma_classification(raw_loc_matrix, time_point, period=3):

    lst = [raw_loc_matrix[time_point - ii] for ii in range(period)]
    intersection = lst[0].intersection(*lst)
    # print("intersection", intersection, len(intersection))

    if len(intersection) >= 2:
        return 1
    else:
        return 0


# ******************************************************************************************* RUN


fig = go.Figure()

# Read localisation types from consolidated file to the localisation_types
f = open(localisations_consolidated_file_path, 'r')
reader = csv.reader(f)
header = next(reader, None)
localisation_types = []
for row in reader:
    localisation_types.append(row[7])

diagram_index = -1
for project_index, project in enumerate(experiments):

    if project_index not in projects_set_to_draw:
        continue

    project_name = project["project"]
    project_folder = project["folder"]

    diagram_index += 1
    x_axis_value = diagram_index * inter_bars_margin
    x_values = []
    y_values = []
    bar_sections = [[[], []], [[], []], [[], []], [[], []]]

    # -- Create/fulfill classifications array --
    classifications_array = []

    # Read classifications for preface or embed
    if project_name == "preface-normal" or project_name == "embed-normal":
        classifications_reader = csv.reader(open(classifications_file_path.format(project_folder=project_folder, project_name=project_name), 'r'))
        classifications_array = [int(row[0]) for row in classifications_reader]
        classifications_array = classifications_array[60 * 24 * 5:60 * 24 * 12]

    # Create fake always-true classifications for loud (which does not have classifier)
    if project_name == "loud-normal":
        classifications_array = [1 for jj in range(TOTAL_DURATION)]

    # Calculate classifications for loud with predictor based on the number consecutive localisation of the same 2 nodes in top 3 suspiciouss nodes
    if project_name == "loud-normal-thr":

        # Read localisation vectors - [0, 1, 0] where [None, Weak, Strong]
        raw_localisations_file_reader = csv.reader(open(localisations_raw_file_path, 'r'))
        raw_localisations_matrix = []
        for row in raw_localisations_file_reader:

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

        # Calculate classifications basing on localisations
        zz = -1
        for localisation_vector in raw_localisations_matrix:
            zz += 1
            classification = get_ma_classification(raw_localisations_matrix, zz)
            classifications_array.append(classification)

    fps = 0
    # Collect localisations to the bar_sections and calculate FPs
    for row_index in range(TOTAL_DURATION):

        localisation_type = 3  # not predicted

        if project_name == "preface-normal" or project_name == "embed-normal":
            if classifications_array[row_index] == 1:
                localisation_type = int(localisation_types[row_index])
                fps += 1

        if project_name == "loud-normal-thr":
            if classifications_array[row_index] == 1:
                localisation_type = 2
                fps += 1

        if project_name == "loud-normal":
            if classifications_array[row_index] == 1:
                localisation_type = int(localisation_types[row_index])

        bar_sections[localisation_type][0].append(x_axis_value)
        bar_sections[localisation_type][1].append(row_index)

    print(project_name, "FPR:", round(fps * 100/TOTAL_DURATION, 2))

    for bar_section_index, bar_section in enumerate(bar_sections):
        size = dash_sizes_by_localisation_type[bar_section_index]
        color = colors_by_project[project_index]
        Xs = bar_section[0]
        Ys = bar_section[1]
        name = project_name

        fig.add_trace(go.Scatter(
            x=Xs,
            y=Ys,
            marker=dict(color=color, size=size),
            marker_symbol="line-ew",
            marker_line_width=marker_line_width,
            marker_line_color=color,
            mode="markers",
            name=name
        ))

fig.update_layout(
    autosize=True,
    width=500,
    height=20000,
    title="",
    xaxis_title="",
    yaxis_title="",
    font=dict(
        family="Courier New, monospace",
        size=24)
)

fig.update_xaxes(showticklabels=False)
fig.layout.showlegend = False

fig.show()
