import csv
import yaml as yaml
from tabulate import tabulate


# **** Paths
root_folder = "../"
configuration = yaml.load(open(root_folder + "resources/configuration/configuration.yml"), Loader=yaml.FullLoader)

data_sets_configuration = yaml.load(open(root_folder + "resources/configuration/data_sets.yml"), Loader=yaml.FullLoader)
consolidated_file_path_pattern  = root_folder + "resources/data/{project_folder}/consolidated_reports/{exp_code}.csv"

# **** Parameters

projects = ["prevent-a", "prevent-e", "premise"]
exp_codes = ["e9", "e7", "e8", "e6", "e5", "e4", "e3", "e1", "e2"]
faults = ["CPU Hog : Random", "CPU Hog : Exponential", "CPU Hog : Linear", "Packet Loss : Random", "Packet Loss : Exponential", "Packet Loss : Linear", "Memory Leak : Random", "Memory Leak : Exponential", "Memory Leak : Linear"]


# **** RUN

for project in projects:

    table_rows = []

    for exp_index, exp_code in enumerate(exp_codes):

        reader = csv.reader(open(consolidated_file_path_pattern.format(project_folder=project, exp_code=exp_code), 'r'))
        header = next(reader, None)
        matrix = []
        for row in reader:
            matrix.append(row)

        earliness = int(matrix[len(matrix) - 1][9])
        stability = int(matrix[len(matrix) - 1][10])

        injection_minute = data_sets_configuration['data_sets'][exp_code]["Injection_minute"]
        failure_minute = data_sets_configuration['data_sets'][exp_code]["Failure_minute"]
        injection_failure_duration = failure_minute - injection_minute
        reaction = injection_failure_duration - earliness

        if earliness == 0:
            reaction = "-"
            stability = "N/A"

        # print(" -", faults[exp_index], ":", injection_failure_duration, ":", reaction, ":", earliness, ":", stability)

        table_rows.append([faults[exp_index], injection_failure_duration, reaction, earliness, stability])

    table = tabulate(table_rows, headers=['Failure : Pattern', 'Injection \n (minutes before failure)', 'Reaction \n (minutes before failure)', 'Earliness \n (minutes before failure)', 'TPR (%)'], tablefmt='orgtbl')
    print("\nPrediction earliness and stability (TPR) for", project, "\n")
    print(table)
