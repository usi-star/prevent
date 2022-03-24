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

consolidated_file_path_pattern = "resources/data/{project_folder}/{project_name}-consolidated-ma-2-outof-3/{project_name}-classifications-e-{fault_id}.csv"

experiments = [{"project": "preface", "folder": "13-preface-data",
                "exp_codes": [1, 2, 3, 4, 5, 7, 8, 9, 10],
                "fault_inj_minutes": [],
                "failure_minutes": []},
               {"project": "embed", "folder": "14-embed-data",
                "exp_codes": [1, 2, 3, 4, 5, 7, 8, 9, 10],  # before was [1, 2, 3, 4, 6, 7, 8, 9, 10]
                "fault_inj_minutes": [],
                "failure_minutes": []},
               {"project": "premise", "folder": "15-premise-data",
                "exp_codes": [1, 2, 3, 4, 5, 7, 8, 9, 10],  # before was [1, 2, 3, 4, 6, 7, 8, 9, 10]
                "fault_inj_minutes": [],
                "failure_minutes": []},
               {"project": "loud", "folder": "16-loud-data",
                "exp_codes": [1, 2, 3, 4, 5, 7, 8, 9, 10],
                "fault_inj_minutes": [],
                "failure_minutes": []}]

for project in experiments:
    for exp_code in project["exp_codes"]:
        exp_code_yaml = "e" + str(exp_code)
        injection_minute = data_sets_configuration['data_sets'][exp_code_yaml]["Injection_minute"]
        failure_minute = data_sets_configuration['data_sets'][exp_code_yaml]["Failure_minute"]

        project["fault_inj_minutes"].append(injection_minute)
        project["failure_minutes"].append(failure_minute)


fault_names = ["MemL-Lin", "MemL-Exp", "MemL-Rnd", "PacL-Lin", "PacL-Exp", "PacL-Rnd", "CpuH-Exp", "CpuH-Lin", "CpuH-Rnd"]
colors_by_project = ["rgb(135,206,250)", "rgb(255,189,85)", "rgb(160,160,160)", "rgb(0, 204, 150)"]
dash_sizes_by_localisation_type = [4, 16, 44, 0.5]
marker_line_width = 3
inter_groups_margin = 3
inter_bars_margin = 3
group_size = inter_groups_margin + len(experiments) * inter_bars_margin


projects_set_to_draw = [0, 1, 3]
# projects_range_to_draw = (1, 1)
# exp_range_to_draw = (0, 8)
# exp_range_to_draw = (0, 2)
# exp_range_to_draw = (3, 5)
exp_range_to_draw = (6, 8)

# ******************************************************************************************* RUN

fig = go.Figure()

for project_index, project in enumerate(experiments):
    project_name = project["project"]
    project_folder = project["folder"]
    project_exp_codes = project["exp_codes"]

    if project_index not in projects_set_to_draw:
        continue

    for exp_index, exp_code in enumerate(project_exp_codes):

        if (exp_index < exp_range_to_draw[0]) or (exp_index > exp_range_to_draw[1]):
            continue

        fault_inj_minute = experiments[project_index]["fault_inj_minutes"][exp_index]
        failure_minute = experiments[project_index]["failure_minutes"][exp_index]
        fault_inj_minute_for_point_on_graph = 19
        x_axis_value = exp_index * group_size + (project_index + 1) * inter_bars_margin

        # Read consolidated file to the matrix
        matrix = []
        file_path = consolidated_file_path_pattern.format(project_folder=project_folder, project_name=project_name, fault_id=exp_code)
        f = open(file_path, 'r')
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            matrix.append(row)

        # Ignore this project->faultType if no predictions
        last_row = len(matrix) - 1
        first_TP_minute = int(matrix[last_row][8])
        if first_TP_minute == -1:
            continue

        x_values = []
        y_values = []
        bar_sections = [[[], []], [[], []], [[], []], [[], []]]

        for row_index in range(len(matrix) - 1):
            print(row_index, matrix[row_index])
            localisation_type = int(matrix[row_index][7])

            bar_sections[localisation_type][0].append(x_axis_value)
            bar_sections[localisation_type][1].append(row_index)

        for bar_section_index, bar_section in enumerate(bar_sections):
            size = dash_sizes_by_localisation_type[bar_section_index]
            color = colors_by_project[project_index]
            Xs = bar_section[0]
            Ys = bar_section[1]
            name = project_name + " : E-" + str(exp_code)

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

        fig.add_trace(go.Scatter(
            x=[x_axis_value],
            y=[fault_inj_minute_for_point_on_graph],
            marker=dict(color="red"),
            marker_symbol="circle",
            marker_line_color="red",
            mode="markers",
            name=name
        ))

# fig.update_yaxes(type="log")

fig.update_layout(
    autosize=True,
    width=2500,
    height=1000,
    title="Time-to-Failure / Prediction / Localisation",
    xaxis_title="Fault-Type-Patterns [Projects: Preface (Blue), Embed (Orange), Premise (Grey)]",
    yaxis_title="Minutes Before Failure",
    font=dict(
        family="Courier New, monospace",
        size=24),
    annotations=[go.layout.Annotation(
            showarrow=False,
            text=exp_code,
            xanchor='right',
            x=15 * exp_index + 3,
            xshift=0,
            yanchor='top',
            y=0.0
            # bgcolor="#0000FF",
            # font=dict(
                # family="Courier New, monospace",
                # size=24,
                # color="#0000FF"
            # )
        ) for exp_index, exp_code in enumerate(fault_names)]
)

fig.update_xaxes(showticklabels=False)
fig.layout.showlegend = False

fig.show()
