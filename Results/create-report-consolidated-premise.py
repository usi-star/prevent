import csv
import os
import yaml as yaml

# **** Paths
root_folder = "../"

configuration = yaml.load(open(root_folder + "resources/configuration/configuration.yml"), Loader=yaml.FullLoader)
data_sets_configuration = yaml.load(open(root_folder + "resources/configuration/data_sets.yml"), Loader=yaml.FullLoader)

kpi_list_file_path = root_folder + "resources/data/kpi-list.csv"
dir_path_classifications_pattern = root_folder + "resources/data/premise/classifications-{model}"
file_path_consolidated_report = root_folder + "resources/data/premise/consolidated_reports/e{exp_code}.csv"

# **** Parameters

file_name_classifications = ["LMT.txt", "LMT.txt"]
# file_name_classifications = ["LMT.txt", "LMT-7_8_9_10.txt"]
fault_free_label = "failurefree"
header_classifications_consolidated = ["Actual state (0 - normal, 1 - faulty)", "Actual classification", "Actual classification MA", "Actual faulty pair", "Localised fault pair", "FP", "TP", "Prediction type (0 - 9)", "First_TP_minute", "Time to failure", "T-TPR", "FPR", "Localisation Rate"]
faults = ["MemL-Exp", "MemL-Lin", "MemL-Rnd", "PacL-Lin", "PacL-Exp", "PacL-Rnd", "CpuH-Exp", "CpuH-Lin", "CpuH-Rnd"]

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
fpr_consider_steady_period_only = False

models = [0, 1]
moving_average_total = 3
moving_average_threshold = 2
fault_injection_minutes = [92, 110, 67, 32, 55, 57, 34, 43, 56]
periods_before_injection = [51, 51, 51, 16, 16, 16, 19, 19, 19]


# **** Functions

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


# **** RUN

# get KPI list
kpi_list = get_kpi_list(kpi_list_file_path)

# get node pairs
cluster_node_pairs = str(configuration['nodes']['pairs']).split(", ")
for ii in range(len(cluster_node_pairs)):
    cluster_node_pairs[ii] = cluster_node_pairs[ii].split(" ")

for model in models:
    for root, dirs, files in os.walk(dir_path_classifications_pattern.format(model=model), topdown=False):
        for name in dirs:
            # Number of False Positives
            FP_Number = 0
            # Number of True Positives
            TP_Number = 0
            # Time To Failure - Number of minutes between first TP and Failure
            TTF = 0
            # Number of minutes between Start and first TP
            minute_of_first_tp = -1
            # distribution of prediction types - [total no true predictions, total none localisations, total weak localisations, total strong localisations]
            exp_predictions = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            # Matrix of data to write to CSV document
            out_csv_lines = []
            # True True Positives Rate - rate of true positives on the span between first TP and Failure
            T_TPR = 0
            # Final distribution of localisation type rates
            prediction_types_rates = [0 for nn in range(len(prediction_types))]

            FP_cache = []
            TP_cache = []

            sets_id = int(name.split("-")[0])
            sets_fault_string = name.split("-")[2].split("_")[0]
            sets_fault_index = int(faults.index(sets_fault_string.replace("@", "-")))
            sets_node_pair = int(name.split("-")[2].split("_")[1])

            print("Fault injection session data:", name, sets_id, sets_fault_index, sets_node_pair)

            exp_fault_inj_minute = fault_injection_minutes[sets_fault_index]
            steady_period_before_injection = periods_before_injection[sets_fault_index]
            last_minute_of_non_steady_period = exp_fault_inj_minute - steady_period_before_injection - 1

            prediction_lines = []
            minute_of_first_tp = -1

            predictions_source_file = open(os.path.join(os.path.join(root, name), file_name_classifications[model]), 'r')
            time_point = 0
            for line in predictions_source_file:

                time_point += 1

                # Current  classification: 0 - normal, 1 - faulty
                # Current actual state: 0 - normal, 1 - faulty
                # Is the current classification a True Positive?
                current_prediction_is_TP = 0
                # Is the current classification a False Positive?
                current_prediction_is_FP = 0

                current_line = line.strip()
                assumed_fault_type = current_line.split("_")[0]

                if assumed_fault_type != fault_free_label:
                    assumed_faulty_resource = int(current_line.split("_")[1])
                else:
                    assumed_faulty_resource = -1

                actual_faulty_resource = sets_node_pair

                # Define Localisation Type
                if assumed_faulty_resource == actual_faulty_resource:
                    current_localisation_type = 2
                else:
                    current_localisation_type = 0

                # Define current_classification using ma 2/3
                current_classification = 0
                current_classification_simple = 0
                if time_point < exp_fault_inj_minute:
                    # Normal period

                    if assumed_fault_type != fault_free_label:
                        current_classification_simple = 1
                        FP_cache.append(1)

                        # Detect true MA classification if the number of true simple classifications in the FP cache is >= the threshold
                        if sum(FP_cache[-moving_average_total:]) >= moving_average_threshold:
                            current_classification = 1
                else:
                    # faulty period

                    if assumed_fault_type != fault_free_label:
                        current_classification_simple = 1
                        TP_cache.append(1)

                        # Detect true MA classification if the number of true simple classifications in the TP cache is >= the threshold
                        if sum(TP_cache[-moving_average_total:]) >= moving_average_threshold:
                            current_classification = 1

                # Consider only the range of [fault-injection - steady_period_before_injection, failure)
                if time_point <= last_minute_of_non_steady_period:
                    if not fpr_consider_steady_period_only:
                        if current_classification == 1:
                            FP_Number += 1
                    continue

                # Define prediction type
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

                out_csv_lines.append([current_actual_state, current_classification_simple, current_classification, actual_faulty_resource, assumed_faulty_resource, current_prediction_is_FP,
                          current_prediction_is_TP, current_prediction_type, "", "", "", "", ""])

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
            predictions_writer = csv.writer(open(file_path_consolidated_report.format(exp_code=str(sets_fault_index + 1)), 'w'))
            predictions_writer.writerow(header_classifications_consolidated)
            for prediction_line in out_csv_lines:
                predictions_writer.writerow(prediction_line)

            predictions_writer.writerow(
                ["", "", "", "", "", "", "", "", minute_of_first_tp, TTF, T_TPR, FPR, prediction_types_rates])
            print(faults[sets_fault_index], ":", [minute_of_first_tp, TTF, T_TPR, FPR], len(out_csv_lines))
