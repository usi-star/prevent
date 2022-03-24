import plotly.graph_objects as go
import csv

# **** Paths
root_folder = "../"
consolidated_file_path_pattern = root_folder + "resources/data/{project_folder}/consolidated_reports/e{exp_code}.csv"

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
                "failure_minutes": []}]

circumference_colors_by_project = ["rgb(135,206,250)", "rgb(255,189,85)", "rgb(160,160,160)"]
circum_colors_by_project = ["rgba(0,0,0, 0)", "rgba(0,0,0, 0)", "rgba(0,0,0, 0)"]
circum_sizes_by_project = [30, 20, 10]
projects_set_to_draw = [0, 1, 2]
experiments_set_to_draw = [1, 2, 3, 4, 5, 6, 7, 8, 9]

fig = go.Figure()
fig.update_layout(
    template="plotly_white",
    title="",
    xaxis_title="False Alarm Rate (%)",
    yaxis_title="True Positive Rate (%)",
    width=800,
    height=800,
    font=dict(
        size=20),
)

for project_index, project in enumerate(experiments):

    if project_index not in projects_set_to_draw:
        continue

    project_name = project["project"]
    project_folder = project["folder"]
    project_exp_codes = project["exp_codes"]
    circumference_color = circumference_colors_by_project[project_index]
    circum_color = circum_colors_by_project[project_index]
    circum_size = circum_sizes_by_project[project_index]

    print("\n", project_name, "\n")

    exp_codes_to_draw = []
    fprs = []
    tprs =  []

    for exp_index, exp_code in enumerate(project_exp_codes):

        if exp_code not in experiments_set_to_draw:
            continue

        exp_codes_to_draw.append(exp_code)

        reader = csv.reader(open(consolidated_file_path_pattern.format(project_folder=project_folder, exp_code=exp_code), 'r'))
        header = next(reader, None)
        matrix = []
        for row in reader:
            matrix.append(row)

        print("Exp FPR/TPR:", exp_code, matrix[len(matrix)-1][11], matrix[len(matrix)-1][10])
        fprs.append(int(matrix[len(matrix)-1][11]))
        tprs.append(int(matrix[len(matrix)-1][10]))

    # Add trace with large marker
    fig.add_trace(
        go.Scatter(
            mode='markers',
            x=fprs,
            y=tprs,
            marker=dict(
                color=circum_color,
                size=circum_size,
                line=dict(
                    color=circumference_color,
                    width=3
                )
            ),
            showlegend=False
        )
    )

fig.show()
