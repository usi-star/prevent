import csv
import sys
import yaml as yaml

# ******************************************************************************************* Configuration

root_folder = "../"

configuration = yaml.load(open(root_folder + "resources/configuration/configuration.yml"), Loader=yaml.FullLoader)
data_sets_configuration = yaml.load(open(root_folder + "resources/configuration/data_sets.yml"), Loader=yaml.FullLoader)

kpi_list_file_path = root_folder + "resources/data/kpi-list.csv"
file_path_classifications_pattern = root_folder + "resources/data/{project_name}/predictions/e{exp_code}.csv"
file_path_localisations_pattern = root_folder + "resources/data/loud/localisations-pairs/e{exp_code}.csv"
file_path_consolidated_report_pattern = root_folder + "resources/data/{project_name}/consolidated_reports/e{exp_code}.csv"

# ******************************************************************************************* Inputs

project_index = int(sys.argv[1])
rank_selection = 325

# ******************************************************************************************* PARAMETERS

periods_before_injection = [51, 51, 51, 16, 16, 16, 19, 19, 19]

experiments = [{"project": "prevent-a", "folder": "prevent-a",
                "exp_codes": [2, 1, 3, 4, 5, 6, 8, 7, 9],
                "fault_inj_minutes": [],
                "failure_minutes": []},
               {"project": "prevent-e", "folder": "prevent-e",
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


faults = ["MemL-Exp", "MemL-Lin", "MemL-Rnd", "PacL-Lin", "PacL-Exp", "PacL-Rnd", "CpuH-Exp", "CpuH-Lin", "CpuH-Rnd"]

project_dir = experiments[project_index]["folder"]
project_name = experiments[project_index]["project"]

project_exp_codes = experiments[project_index]["exp_codes"]
project_fault_inj_minutes = experiments[project_index]["fault_inj_minutes"]
project_failure_minutes = experiments[project_index]["failure_minutes"]

header_classifications_consolidated = ["Actual state (0 - normal, 1 - faulty)", "Actual classification", "Actual classification MA", "Actual faulty pair", "Localised fault pair", "FP", "TP", "Prediction type (0 - 9)", "First_TP_minute",
                                       "Time to failure", "True TPR", "FPR", "Localisation Rate"]

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
fpr_consider_steady_period_only = True

# ******************************************************************************************* FUNCTIONS


def get_kpi_list(_kpi_list_file_path):
    _fil = open(_kpi_list_file_path, 'r')
    _reader = csv.reader(_fil)
    _header = next(_reader, None)

    return _header


def determine_localisation_type(localisation_vector):
    for index, value in enumerate(localisation_vector):
        if value == 1:
            return index

    return -1


# ******************************************************************************************* RUN

# Loop fault types/patterns of the project
for exp_index, exp_code in enumerate(project_exp_codes):

    steady_period_before_injection = periods_before_injection[exp_index]
    exp_fault_inj_minute = project_fault_inj_minutes[exp_index]
    last_minute_of_non_steady_period = exp_fault_inj_minute - steady_period_before_injection - 1
    exp_failure_minute = project_failure_minutes[exp_index]
    faulty_period_duration = (exp_failure_minute - 1) - (exp_fault_inj_minute - 1)

    print(exp_code, ":", steady_period_before_injection, last_minute_of_non_steady_period, exp_fault_inj_minute, exp_failure_minute, faulty_period_duration)

    # Number of False Positives
    FP_Number = 0

    # Number of True Positives
    TP_Number = 0

    # Time To Failure - Number of minutes between first TP and Failure
    TTF = 0

    # Number of minutes between Start and first TP
    minute_of_first_tp = -1

    # Distribution of prediction types - [total no true predictions, total none localisations, total weak localisations, total strong localisations]
    exp_predictions = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # Matrix of data to write to CSV document
    out_csv_lines = []

    # Matrix of localisation types for top 3 suspicious nodes per each timestamp - list of vectors like [x, y, z] where x, y, and belongs to {0, 1, 2},
    # 0 - no localisation, 1 - weak localisation, 2 - strong localisation
    # (covers the period from the beginning of the steady period until failure point)
    localisations_matrix = []

    # List of classifications (cover full period of experiment)
    # 0 - normal, 1 - faulty
    classifications_list = []

    # True True Positives Rate - rate of true positives on the span between first TP and Failure
    T_TPR = 0

    # Final distribution of localisation type rates
    prediction_types_rates = [0 for nn in range(len(prediction_types))]

    # Read the list of classifications.
    classifications_file_reader = csv.reader(open(file_path_classifications_pattern.format(project_name=project_name, exp_code=exp_code), 'r'))
    for classification in classifications_file_reader:
        classifications_list.append(int(classification[0]))

    # Read the matrix of localisations from Loud
    localisations_file_reader = csv.reader(open(file_path_localisations_pattern.format(exp_code=exp_code), 'r'))
    localisations_file_header = next(localisations_file_reader, None)
    for row in localisations_file_reader:
        localisations_matrix.append([int(row[3]), int(row[2]), int(row[1])])

    # Loop all time points in of the experiment (minutes 1 - failure)
    time_point = 0
    classifications_file_reader = csv.reader(open(file_path_classifications_pattern.format(project_name=project_name, exp_code=exp_code), 'r'))
    for current_classification in classifications_list:

        time_point += 1
        # Consider only the range of [fault-injection - steady_period_before_injection, failure)
        if time_point <= last_minute_of_non_steady_period:
            if not fpr_consider_steady_period_only:
                if current_classification == 1:
                    FP_Number += 1
            continue

        if time_point >= exp_failure_minute:
            continue

        # Current  classification: 0 - normal, 1 - faulty
        # Current actual state: 0 - normal, 1 - faulty
        # Is the current classification a True Positive?
        current_prediction_is_TP = 0
        # Is the current classification a False Positive?
        current_prediction_is_FP = 0

        # Get localisation type
        # current_localisation_type = : 0 - neither faulty node localised, 1 - 1 of the faulty nodes localised, 2 - both faulty nodes localised
        index_in_localisation_vector = time_point - last_minute_of_non_steady_period - 1
        print(exp_code, ":", time_point, last_minute_of_non_steady_period, index_in_localisation_vector)
        localisation_vector = localisations_matrix[index_in_localisation_vector]
        current_localisation_type = determine_localisation_type(localisation_vector)

        if time_point < exp_fault_inj_minute:

            # Normal period after the non-steady period
            current_actual_state = 0

            if current_classification == 0:
                current_prediction_type = 0
            else:
                current_prediction_type = 1

                current_prediction_is_FP = 1
                FP_Number += 1

        else:
            # Faulty period
            current_actual_state = 1

            if current_classification == 1:

                # Current prediction is TRUE Positive IF current classification is TRUE AND current localisation is {Weak or Strong}
                if current_localisation_type == 1 or current_localisation_type == 2:
                    current_prediction_is_TP = 1
                    TP_Number += 1

                    # Fix the first TP point
                    if TP_Number == 1:
                        minute_of_first_tp = time_point
                else:

                    # Current prediction is FALSE Positive IF current classification is TRUE AND current localisation is NOT {Weak or Strong}
                    current_prediction_is_FP = 1

            if TP_Number == 0:
                # Faulty period < First TP

                if current_classification == 0:
                    # Mauro: current_prediction_type = 2
                    # Giovanni: current_prediction_type = 6
                    current_prediction_type = 2
                else:
                    if current_localisation_type == 0:
                        current_prediction_type = 3

                    if current_localisation_type == 1:
                        current_prediction_type = 4

                    if current_localisation_type == 2:
                        current_prediction_type = 5
            else:
                # Faulty period >= First TP

                # Increment Time-to-Failure counter on each time point if there is already at least 1 True-Positive
                TTF += 1

                if current_classification == 0:
                    current_prediction_type = 6
                else:
                    if current_localisation_type == 0:
                        current_prediction_type = 7

                    if current_localisation_type == 1:
                        current_prediction_type = 8

                    if current_localisation_type == 2:
                        current_prediction_type = 9

        out_csv_lines.append([current_actual_state, "NA", current_classification, "NA", "NA", current_prediction_is_FP, current_prediction_is_TP, current_prediction_type, localisation_vector[2], localisation_vector[1], localisation_vector[0], "", ""])

        exp_predictions[current_prediction_type] += 1

    if fpr_consider_steady_period_only:
        FPR = int(FP_Number / steady_period_before_injection * 100)
    else:
        FPR = int(FP_Number / (exp_fault_inj_minute - 1) * 100)

    if TP_Number > 0:
        T_TPR = int(TP_Number / TTF * 100)
        for prediction_type_index in range(len(prediction_types)):
            prediction_types_rates[prediction_type_index] = round(exp_predictions[prediction_type_index] / sum(exp_predictions), 2)

    # Create and write to the file with the prediction types
    predictions_writer = csv.writer(open(file_path_consolidated_report_pattern.format(project_name=project_name, exp_code=exp_code), 'w'))
    predictions_writer.writerow(header_classifications_consolidated)
    for prediction_line in out_csv_lines:
        predictions_writer.writerow(prediction_line)

    predictions_writer.writerow(["", "", "", "", "", "", "", "", minute_of_first_tp, TTF, T_TPR, FPR, prediction_types_rates])
    print(faults[exp_code - 1], ":", [minute_of_first_tp, TTF, T_TPR, FPR])
