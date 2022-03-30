import plotly.graph_objects as go
import csv
import yaml as yaml


# **** Paths
root_folder = "../"

configuration = yaml.load(open(root_folder + "resources/configuration/configuration.yml"), Loader=yaml.FullLoader)
data_sets_configuration = yaml.load(open(root_folder + "resources/configuration/data_sets.yml"), Loader=yaml.FullLoader)

consolidated_file_path_pattern  = root_folder + "resources/data/{project_folder}/consolidated_reports/e{exp_code}.csv"


# **** Parameters

experiments = [{"project": "prevent-a", "folder": "prevent-a",
                "exp_codes": [2, 1, 3, 4, 5, 6, 8, 7, 9],
                "fault_inj_minutes": [],
                "failure_minutes": []},
               {"project": "prevent-e", "folder": "prevent-e",
                "exp_codes": [2, 1, 3, 4, 5, 6, 8, 7, 9],
                "fault_inj_minutes": [],
                "failure_minutes": []},
               {"project": "premise", "folder": "premise",
                "exp_codes": [2, 1, 3, 4, 5, 6, 8, 7, 9],
                "fault_inj_minutes": [],
                "failure_minutes": []},
               {"project": "loud", "folder": "loud",
                "exp_codes": [2, 1, 3, 4, 5, 6, 8, 7, 9],
                "fault_inj_minutes": [],
                "failure_minutes": []}]

for project in experiments:
    for exp_code in project["exp_codes"]:
        exp_code_yaml = "e" + str(exp_code)
        injection_minute = data_sets_configuration['data_sets'][exp_code_yaml]["Injection_minute"]
        failure_minute = data_sets_configuration['data_sets'][exp_code_yaml]["Failure_minute"]

        project["fault_inj_minutes"].append(injection_minute)
        project["failure_minutes"].append(failure_minute)

def get_fault_name_by_exp_code(experiment_code):
    fault_names = ["MemL-Exp", "MemL-Lin", "MemL-Rnd", "PacL-Lin", "PacL-Exp", "PacL-Rnd", "CpuH-Exp", "CpuH-Lin", "CpuH-Rnd"]
    return fault_names[experiment_code - 1]

colors_by_project = ["rgb(135,206,250)", "rgb(255,189,85)", "rgb(160,160,160)"]

#   Predictions types
#   Type	Period	Classification	Localisation	Line-width Comment
#   0	    0	    0	            any	            0
#   1	    0	    1	            any	            4           sq-dot
#   2	    1	    0	            any	            0
#   3	    1	    1	            0	            4           sq-dot
#   4	    1	    1	            1	            16
#   5	    1	    1	            2	            44
#   6	    2	    0	            any	            0.5         line
#   7	    2	    1	            0	            4           sq-dot
#   8	    2	    1	            1	            16
#   9	    2	    1	            2	            44

prediction_types = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
dash_sizes_by_prediction_type = [0.001, 4, 0.001, 4, 16, 44, 0.5, 4, 16, 44]

periods_before_injection = [51, 51, 51, 16, 16, 16, 19, 19, 19]

projects_set_to_draw = [0, 1, 2]
experiments_set_to_draw = [1, 2, 3, 4, 5, 6, 7, 8, 9]

# Graph visualisation settings
marker_line_width = 3
inter_groups_margin = 3
inter_bars_margin = 3
x_shift = 9
graph_width = 3000
graph_height = 1000

group_size = inter_groups_margin + len(projects_set_to_draw) * inter_bars_margin


# **** RUN

fig = go.Figure()

for project_index, project in enumerate(experiments):

    if project_index not in projects_set_to_draw:
        continue

    project_name = project["project"]
    project_folder = project["folder"]
    project_exp_codes = project["exp_codes"]

    exp_codes_to_draw = []
    for exp_index, exp_code in enumerate(project_exp_codes):

        if exp_code not in experiments_set_to_draw:
            continue

        exp_codes_to_draw.append(exp_code)

        x_values = []
        y_values = []
        bar_sections = [
            [[], []],
            [[], []],
            [[], []],
            [[], []],
            [[], []],
            [[], []],
            [[], []],
            [[], []],
            [[], []],
            [[], []]
        ]

        period_before_injection = periods_before_injection[exp_index]
        fault_inj_minute = experiments[project_index]["fault_inj_minutes"][exp_index]
        failure_minute = experiments[project_index]["failure_minutes"][exp_index]

        x_axis_value = (len(exp_codes_to_draw) - 1) * group_size + (project_index + 1) * inter_bars_margin

        # Load consolidated file to the matrix
        reader = csv.reader(open(consolidated_file_path_pattern.format(project_folder=project_folder, exp_code=exp_code), 'r'))
        header = next(reader, None)
        matrix = []
        for row in reader:
            matrix.append(row)

        # The period [fault_injection - steady period before injection, failure)
        target_period_len = len(matrix) - 1
        if (int(period_before_injection) + int(failure_minute) - int(fault_inj_minute)) != target_period_len:
            print(project_name, exp_code, period_before_injection, failure_minute, fault_inj_minute, target_period_len)
            exit("target period is not correct")

        # print(project_name, exp_code, fault_inj_minute, failure_minute)

        # Point before start of the target period
        start_minute_for_point_on_graph = target_period_len + 1
        fault_inj_minute_for_point_on_graph = target_period_len - period_before_injection

        # Collect prediction types to the bar sections
        for row_index in range(target_period_len):
            current_prediction_type = int(matrix[row_index][7])

            graph_row_index = target_period_len - row_index

            bar_sections[current_prediction_type][0].append(x_axis_value)
            bar_sections[current_prediction_type][1].append(graph_row_index)

        for bar_section_index, bar_section in enumerate(bar_sections):
            size = dash_sizes_by_prediction_type[bar_section_index]
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

        if exp_index < len(project_exp_codes) - 1:
            fig.add_vrect(x0=group_size * len(exp_codes_to_draw), x1=group_size * len(exp_codes_to_draw) )

        Xs = [group_size * 9]
        Ys = [0]

        fig.add_trace(go.Scatter(
            x=Xs,
            y=Ys,
            marker=dict(color="black", size=0.001),
            marker_symbol="line-ew",
            marker_line_width=marker_line_width,
            marker_line_color="black",
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

        fig.add_trace(go.Scatter(
            x=[x_axis_value],
            y=[start_minute_for_point_on_graph],
            marker=dict(color="black"),
            marker_symbol="circle",
            marker_line_color="black",
            mode="markers",
            name=name
        ))

fig.update_layout(
    autosize=True,
    width=graph_width,
    # height=graph_height * 1.6,
    # height=graph_height * 0.8,
    height=graph_height,
    title="",
    xaxis_title="",
    yaxis_title="Minutes",
    font=dict(
        family="Courier New, monospace",
        size=24),
    annotations=[go.layout.Annotation(
            showarrow=False,
            text=get_fault_name_by_exp_code(exp_code),
            xanchor='right',
            x=group_size * exp_index + x_shift,
            xshift=0,
            yanchor='top',
            y=0.0
            # bgcolor="#0000FF",
            # font=dict(
                # family="Courier New, monospace",
                # size=24,
                # color="#0000FF"
            # )
        ) for exp_index, exp_code in enumerate(exp_codes_to_draw)]
)

fig.update_xaxes(showticklabels=False)
fig.layout.showlegend = False

fig.show()
