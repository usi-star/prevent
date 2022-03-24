import csv
import json
import logging
import os
from datetime import datetime
from typing import Dict
import numpy as np
# from ruamel.yaml import YAML
import yaml as yaml
from datetime import timezone

def parse_yaml(file_path) -> Dict:
    """
    Parse a YAML file and load into a Python dictionary.

    :param str file_path: The file path of the YAML file.
    :return: The Python dictionary.
    :rtype: Dict
    """
    # yaml = YAML()
    with open(file_path, mode='r') as file:
        result = yaml.load(file)
    return result


def set_logging(log_file_path, loggingFormat='%(asctime)s %(levelname)-4s: %(message)s'):
    loggingFormat = loggingFormat
    logging.basicConfig(filename=log_file_path, filemode='a', format=loggingFormat, level=logging.INFO,
                        datefmt='%y.%m.%d.%H.%M')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(loggingFormat))
    logging.getLogger('').addHandler(console)


def get_total_of_negatives_and_positives(fault_injection_minute, failure_minute):
    return fault_injection_minute, failure_minute - fault_injection_minute


def get_region_type(current_minute, fault_injection_minute, failure_minute):
    if current_minute < fault_injection_minute:
        return "negatives"
    elif fault_injection_minute <= current_minute < failure_minute:
        return "positives_before_failure"
    else:
        return "positives_after_failure"


def scatterplot(plt, minutes, anomalies_numbers, predictions, fault_injection_minute, failure_minute,
                predictions_visualization_file_path, title):
    fig, ax = plt.subplots(figsize=(20, 12))

    ax.plot(minutes, anomalies_numbers, color="MediumPurple", alpha=0.50)
    ax.scatter(minutes, predictions, alpha=0.60, label="Predictions")

    # adds a title and axes labels
    text_arr = str(title).split(" ")

    if len(text_arr) > 4:
        text = "\n\nPrecision: " + text_arr[4] + "\n Minutes before failre: " + text_arr[
            5] + "\n" + "Prediction Stability Rate: " + text_arr[6] + "\n" + "FP Rate: " + text_arr[7]
    else:
        text = ""

    # ax.set_title(title + text, fontsize=30)
    ax.set_xlabel('Minutes', fontsize=30)
    ax.set_ylabel('Anomalies', fontsize=30)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)

    # removing top and right borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # adds major grid lines
    ax.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)

    plt.axvspan(fault_injection_minute, failure_minute, color="pink", alpha=0.3)

    ax.legend(prop={'size': 24})

    plt.text(0.1, 0.1, text, fontsize=24)

    plt.savefig(predictions_visualization_file_path)


def get_anomalies_numbers(anomalies_file_path, experiment_duration):
    numbers = []
    with open(anomalies_file_path, 'r') as json_file:
        anomalies_json = json.loads(json_file.read())

        for i in range(len(anomalies_json)):
            if i == experiment_duration:
                break
            numbers.append(len(anomalies_json[i]))
    return numbers


def get_input_thrs(anomalies_set_thr):
    anomalies_set_thr = str(anomalies_set_thr)

    if anomalies_set_thr == "auto":
        anomalies_set_thr_str = anomalies_set_thr
        return anomalies_set_thr, anomalies_set_thr_str

    if anomalies_set_thr == "scale":
        anomalies_set_thr_str = anomalies_set_thr
        return anomalies_set_thr, anomalies_set_thr_str

    if "." in anomalies_set_thr:
        anomalies_set_thr = float(anomalies_set_thr)
    else:
        if anomalies_set_thr.startswith("0"):
            anomalies_set_thr_str = anomalies_set_thr
            anomalies_set_thr = int(anomalies_set_thr)
            return anomalies_set_thr, anomalies_set_thr_str
        else:
            anomalies_set_thr = int(anomalies_set_thr)

    if anomalies_set_thr < 1:
        anomalies_set_thr_str = str(anomalies_set_thr).replace(".", "")
    else:
        anomalies_set_thr_str = str(anomalies_set_thr)

    return anomalies_set_thr, anomalies_set_thr_str


def get_time_range_and_delta(start_time, end_time, time_delta):
    start_time_arr = start_time.split(".")
    end_time_arr = end_time.split(".")
    for ii in range(len(start_time_arr)):
        start_time_arr[ii] = int(start_time_arr[ii])
        end_time_arr[ii] = int(end_time_arr[ii])

    start_datetime = datetime(start_time_arr[0], start_time_arr[1], start_time_arr[2], start_time_arr[3],
                              start_time_arr[4])
    end_datetime = datetime(end_time_arr[0], end_time_arr[1], end_time_arr[2], end_time_arr[3], end_time_arr[4])
    time_delta = int(time_delta)

    return start_datetime, end_datetime, time_delta


def scatterplot_anomalies(plt, minutes, anomalies_numbers, ouput_file_path, title):
    fig, ax = plt.subplots(figsize=(50, 10))

    print(len(minutes))
    print(len(anomalies_numbers))

    ax.plot(minutes, anomalies_numbers, color="MediumPurple", alpha=0.50)

    # adds a title and axes labels
    ax.set_title(title)
    ax.set_xlabel('Minutes')
    ax.set_ylabel('Anomalies')

    # removing top and right borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # adds major grid lines
    ax.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)

    marked = False
    for ii in minutes:
        if ii % 1440 == 0:
            if not marked:
                marked = True
                plt.axvspan(ii, ii + 1440, color="pink", alpha=0.3)
            else:
                marked = False

    ax.legend()

    plt.savefig(ouput_file_path)


def scatterplot_anomalies_compare(plt, minutes, anomalies_numbers_1, anomalies_numbers_2, ouput_file_path, title,
                                  legend_1, legend_2):
    fig, ax = plt.subplots(figsize=(50, 10))

    ax.plot(minutes, anomalies_numbers_1, color="MediumPurple", alpha=0.50)
    ax.plot(minutes, anomalies_numbers_2, color="salmon", alpha=0.50)

    # adds a title and axes labels
    ax.set_title(title)
    ax.set_xlabel('Minutes')
    ax.set_ylabel('Anomalies')

    # removing top and right borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # adds major grid lines
    ax.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)

    marked = False
    for ii in minutes:
        if ii % 1440 == 0:
            if not marked:
                marked = True
                plt.axvspan(ii, ii + 1440, color="pink", alpha=0.3)
            else:
                marked = False

    ax.legend([legend_1, legend_2])

    plt.savefig(ouput_file_path)


def scatterplot_profile(plt, minutes, load_value, ouput_file_path, title):
    fig, ax = plt.subplots(figsize=(50, 10))

    print(len(minutes))
    print(len(load_value))

    ax.plot(minutes, load_value, color="MediumPurple", alpha=0.50)

    print("done")

    # adds a title and axes labels
    ax.set_title(title)
    ax.set_xlabel('Minutes')
    ax.set_ylabel('Load')

    plt.xticks(np.arange(min(minutes), max(minutes) + 1, 16.0))

    # removing top and right borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # adds major grid lines
    ax.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)

    marked = False
    for ii in minutes:
        if ii % 1440 == 0:
            if not marked:
                marked = True
                plt.axvspan(ii, ii + 1440, color="pink", alpha=0.3)
            else:
                marked = False
    ax.legend()
    plt.savefig(ouput_file_path)


def visualize_re_mse(plt, values_arr):
    fig, ax = plt.subplots(figsize=(40, 25))

    minutes = [x for x in range(len(values_arr))]
    ax.plot(minutes, values_arr, color="MediumPurple", alpha=0.50)
    # ax.scatter(minutes, predictions, alpha=0.60, label="Predictions")

    # adds a title and axes labels
    ax.set_title("RE MSE", fontsize=28)

    ax.set_xlabel('Minutes')
    ax.set_ylabel('RE MSE')

    # removing top and right borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # adds major grid lines
    ax.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)

    # plt.axvspan(fault_injection_minute, failure_minute, color="pink", alpha=0.3)

    ax.legend()

    # plt.text(0.1, 0.1, text, fontsize=18)

    # plt.savefig(predictions_visualization_file_path)

    plt.show()


def get_records_number(p_data_sets_configuration, p_data_set_code):
    l_start_time = p_data_sets_configuration['data_sets'][p_data_set_code]['start_time']
    l_end_time = p_data_sets_configuration['data_sets'][p_data_set_code]['end_time']
    l_time_delta = p_data_sets_configuration['data_sets'][p_data_set_code]['time_delta']

    start_datetime, end_datetime, time_delta = get_time_range_and_delta(l_start_time, l_end_time, l_time_delta)

    records_num = int((end_datetime - start_datetime).total_seconds() / 60)

    return records_num


def keras_visualize_re_mse(plt, values_arr):
    fig, ax = plt.subplots(figsize=(40, 25))

    minutes = [x for x in range(len(values_arr))]
    ax.plot(minutes, values_arr, color="MediumPurple", alpha=0.50)
    # ax.plot(minutes, line, color="Red", alpha=0.50)
    # ax.scatter(minutes, predictions, alpha=0.60, label="Predictions")

    # adds a title and axes labels
    ax.set_title("RE MSE", fontsize=28)

    ax.set_xlabel('Minutes')
    ax.set_ylabel('RE MSE')

    # removing top and right borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # adds major grid lines
    ax.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)

    # plt.axvspan(fault_injection_minute, failure_minute, color="pink", alpha=0.3)

    ax.legend()

    # plt.text(0.1, 0.1, text, fontsize=18)

    # plt.savefig(predictions_visualization_file_path)

    plt.show()


def get_hist(file_path):
    mse_history = []

    with open(file_path, 'r') as file_in:
        for line in file_in:
            mse = float(line.strip('\n'))
            mse_history.append(mse)

    return mse_history


def load_data(input_data_set_file="resources/titles.csv"):
    with open(input_data_set_file, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        header = next(reader)

    return header


def localizations_visualization(plt, minutes, anomalies_numbers, localizations_and, localizations_xor,
                                localizations_neither, visualization_file_path, title, and_perc, xor_perc, neith_perc,
                                annotations):
    fig, ax = plt.subplots(figsize=(40, 25))

    ax.set_yscale('log')

    ax.plot(minutes, anomalies_numbers, color="MediumPurple", alpha=0.50)
    ax.scatter(minutes, localizations_and, color="Red", alpha=0.60, label="Master AND Slave (" + str(and_perc) + "%)",
               s=150)
    ax.scatter(minutes, localizations_xor, color="Blue", alpha=0.60, label="Master XOR Slave (" + str(xor_perc) + "%)",
               s=150)
    ax.scatter(minutes, localizations_neither, color="Green", alpha=0.60,
               label="Neither localized (" + str(neith_perc) + "%)", s=150)

    # adds a title and axes labels
    text_arr = str(title).split(" ")
    text = ""

    ax.set_title(title + text, fontsize=28)
    ax.set_xlabel('Minutes', fontsize=36)
    ax.set_ylabel('Number of anomalous KPIs', fontsize=36)

    # removing top and right borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # adds major grid lines
    ax.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)

    ax.legend()
    ax.legend(loc=2, prop={'size': 36})

    plt.text(0.1, 0.1, text, fontsize=28)
    plt.xticks(fontsize=28)
    plt.yticks(fontsize=28)

    for i, annotation in enumerate(annotations):

        if localizations_and[i] is not None:
            ax.annotate(annotation, (minutes[i], localizations_and[i]), fontsize=20)

        if localizations_xor[i] is not None:
            ax.annotate(annotation, (minutes[i], localizations_xor[i]), fontsize=20)

        if localizations_neither[i] is not None:
            ax.annotate(annotation, (minutes[i], localizations_neither[i]), fontsize=20)

    plt.savefig(visualization_file_path)


def localizations_percentages_visualization(plt, rank_selection_list, and_perc, xor_perc, neith_perc,
                                            visualization_file_path, title):
    fig, ax = plt.subplots(figsize=(40, 25))

    # ax.set_yscale('log')

    ax.plot(rank_selection_list, and_perc, color="Red", alpha=0.50, label="Master AND Slave")
    ax.plot(rank_selection_list, xor_perc, color="Blue", alpha=0.50, label="Master XOR Slave")
    ax.plot(rank_selection_list, neith_perc, color="Green", alpha=0.50, label="Neither localized")

    ax.set_title(title, fontsize=28)
    ax.set_xlabel('Rank Selection', fontsize=36)
    ax.set_ylabel('Percentage out of all predictions', fontsize=36)

    # removing top and right borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # adds major grid lines
    ax.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)

    ax.legend()
    ax.legend(loc=2, prop={'size': 36})

    # plt.text(0.1, 0.1, text, fontsize=28)
    plt.xticks(fontsize=28)
    plt.yticks(fontsize=28)

    plt.savefig(visualization_file_path)


def localizations_cumul_stability_visualization(plt, minutes, pairs_cum_values, visualization_file_path, title):
    fig, ax = plt.subplots(figsize=(40, 25))

    # ax.set_yscale('log')

    for ii in range(len(pairs_cum_values)):
        ax.plot(minutes, pairs_cum_values[ii], alpha=0.90,
                label=str(ii) + ": " + str(pairs_cum_values[ii][len(pairs_cum_values[ii]) - 1]))

    # adds a title and axes labels
    text_arr = str(title).split(" ")
    text = ""

    ax.set_title(title + text, fontsize=28)
    ax.set_xlabel('Minutes', fontsize=36)
    ax.set_ylabel('Cumulative number of occurrence in TOP 3', fontsize=36)

    # removing top and right borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # adds major grid lines
    ax.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)

    ax.legend()
    ax.legend(loc=2, prop={'size': 36})

    plt.text(0.1, 0.1, text, fontsize=28)
    plt.xticks(fontsize=28)
    plt.yticks(fontsize=28)

    plt.savefig(visualization_file_path)


# convert datetime object to timestamp in UTC
# DateTime -> Timestamp
def datetime_timestamp_utc(dt_object):
    timestamp = int(dt_object.replace(tzinfo=timezone.utc).timestamp())
    return timestamp


# convert timestamp to datetime in UTC
# Timestamp -> DateTime
def timestamp_to_datetime_utc(timestamp):
    dt_object = datetime.utcfromtimestamp(timestamp)
    return dt_object


# convert datetime string (example: 2020.04.11.16.01) to timestamp in UTC
# DateTime -> Timestamp
def datetime_string_timestamp_utc(dt_string):
    dt_object = datetime.strptime(dt_string, '%Y.%m.%d.%H.%M')
    timestamp = int(dt_object.replace(tzinfo=timezone.utc).timestamp())
    return timestamp
