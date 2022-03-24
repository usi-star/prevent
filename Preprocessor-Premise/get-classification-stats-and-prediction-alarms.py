import csv
import json
import os
import sys
import requests
import pandas as pd
from datetime import datetime
import utils
from ruamel.yaml import YAML
from typing import Dict
from shutil import copyfile
import statistics

# ******************************************************************************************* Configuration

script_dir = os.path.dirname(os.path.abspath(__file__))

configuration_file_path = os.path.join(script_dir, 'resources/configuration/configuration.yml')
configuration: Dict = utils.parse_yaml(configuration_file_path)

data_sets_configuration_file_path = os.path.join(script_dir, 'resources/configuration/data_sets.yml')
data_sets_configuration: Dict = utils.parse_yaml(data_sets_configuration_file_path)

# ******************************************************************************************* Parameters

model_codes_list = [1, 2]
fault_code_prefix = "e"
fault_ids_list = [[7, 8, 9, 10], [1, 2, 3, 4, 6]]
cache_length = 3
threshold = 2
stats_header = ["Fault Code", "T-TPR", "FPR", "Minutes before failure"]

in_classifications_file_path_pattern = "resources/data/8-classifications/classifications-model-{model_code}-test-set-{fault_code}.csv"
out_stats_file_path = "resources/data/10-stats/stats.csv"
out_predictions_file_path_pattern = "resources/data/9-prediction-alarms/Predictions_{fault_code}.csv"

# ******************************************************************************************* Functions


def get_times(experiment_data_set_code, data_sets_configuration):
    start_time = data_sets_configuration['data_sets'][experiment_data_set_code]["start_time"]
    fault_injection_time = data_sets_configuration['data_sets'][experiment_data_set_code]["fault_injection_time"]
    failure_time = data_sets_configuration['data_sets'][experiment_data_set_code]["failure_time"]

    start_time = datetime.strptime(start_time, '%Y.%m.%d.%H.%M')
    fault_injection_time = datetime.strptime(fault_injection_time, '%Y.%m.%d.%H.%M')
    failure_time = datetime.strptime(failure_time, '%Y.%m.%d.%H.%M')

    start_timestamp = utils.datetime_timestamp_utc(start_time)
    fault_injection_timestamp = utils.datetime_timestamp_utc(fault_injection_time)
    failure_timestamp = utils.datetime_timestamp_utc(failure_time)

    start_minute = 1
    fault_injection_minute = int((fault_injection_timestamp - start_timestamp) / 60) + start_minute
    failure_minute = int((failure_timestamp - start_timestamp) / 60) + start_minute

    return start_minute, fault_injection_minute, failure_minute


def get_current_period(current_minute, start_minute, fault_injection_minute, cache_length):

    if current_minute < fault_injection_minute:
        if (current_minute - (cache_length - 1)) >= start_minute:
            period_current = "normal"
        else:
            period_current = "ignore"
    else:
        if (current_minute - (cache_length - 1)) >= fault_injection_minute:
            period_current = "anomalous"
        else:
            period_current = "ignore"

    return period_current


def is_threshold_reached(classification_history, row_index, cache_length, threshold):

    number_of_suspects = 0

    for ii in range(row_index - (cache_length - 1), row_index + 1):
        if classification_history[ii] != "n":
            number_of_suspects += 1

    if number_of_suspects >= threshold:
        return True
    else:
        return False


def get_result(current_period, classification):

    result = "ignore"

    if current_period == "normal":
        if classification != "n":
            result = "FP"

    if current_period == "anomalous":
        if classification != "n":
            result = "TP"

    return result


# ******************************************************************************************* RUN

outfile = open(out_stats_file_path, 'w')
writer = csv.writer(outfile)
writer.writerow(stats_header)

summary = []

for model_code in model_codes_list:
    for fault_id in fault_ids_list[model_code - 1]:

        fault_code = fault_code_prefix + str(fault_id)

        classification_file_path = in_classifications_file_path_pattern.format(model_code=model_code, fault_code=fault_code)
        start_minute, fault_injection_minute, failure_minute = get_times(fault_code, data_sets_configuration)

        # timestamps from start (minute 1) to the minute of failure - 1
        total_duration = failure_minute - start_minute

        f = open(classification_file_path, 'r')
        reader = csv.reader(f)
        header = next(reader, None)

        classification_history = []
        for row in reader:
            classification_history.append(str(row[2]).split(":")[1])

        T_TPR_list = []
        FPR_list = []
        minutes_before_failure_list = []

        FP_count = 0
        TP_count = 0
        first_TP_detected = False

        predictions = []

        minutes_before_failure = 0

        current_minute = 0
        for row_index in range(0, total_duration):
            current_minute += 1
            prediction_alerted = 0

            if is_threshold_reached(classification_history, row_index, cache_length, threshold):

                current_period = get_current_period(current_minute, start_minute, fault_injection_minute, cache_length)
                result = get_result(current_period, classification_history[row_index])

                if result == "FP":
                    FP_count += 1

                if result == "TP":
                    prediction_alerted = 1

                    TP_count += 1

                    if TP_count == 1:
                        first_TP_detected = True
                        minutes_before_failure = failure_minute - current_minute

            predictions.append(prediction_alerted)

        FPR = round((FP_count / (fault_injection_minute - start_minute)) * 100)
        if minutes_before_failure > 0:
            T_TPR = round((TP_count / minutes_before_failure) * 100)
        else:
            T_TPR = 0

        record = [fault_code, T_TPR, FPR, minutes_before_failure]
        writer.writerow(record)

        T_TPR_list.append(T_TPR)
        FPR_list.append(FPR)
        minutes_before_failure_list.append(minutes_before_failure)

        predictions_file_path = out_predictions_file_path_pattern.format(fault_code=fault_code)
        predictions_outfile = open(predictions_file_path, 'w')
        predictions_writer = csv.writer(predictions_outfile)

        for prediction in predictions:
            predictions_writer.writerow([prediction])
