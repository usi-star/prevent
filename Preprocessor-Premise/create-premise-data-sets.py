import csv
import os
from datetime import datetime
import utils
import yaml as yaml


# **** Configuration

root_folder = "../"
configuration = yaml.load(open(root_folder + "resources/configuration/configuration.yml"), Loader=yaml.FullLoader)
data_sets_configuration = yaml.load(open(root_folder + "resources/configuration/data_sets.yml"), Loader=yaml.FullLoader)

# **** Parameters

kpi_list_file_path = root_folder + "resources/data/kpi-list.csv"
anomalies_file_path_pattern = root_folder + "resources/data/premise/anomalies-shuffled/e{fault_code}-{pair_id}.csv"

premise_exp_folder_path_pattern_faulty = root_folder + "Toolset-Premise/data/anomalies-{model}/{data_set_type}/{id}-10.40.7.172-{fault_type}@{fault_pattern}_{faulty_pair_id}_{fault_pattern}"
premise_exp_folder_path_pattern_normal = root_folder + "Toolset-Premise/data//anomalies-{model}/{data_set_type}/{id}-10.40.7.172-failurefree_x_x"

premise_exp_file_name_pattern = "{minute_of_experiment}.txt"
premise_exp_file_row_pattern = "('{pair_id}', 'x', '{metric}')\n"

pair_id_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
fault_code_list = [[[1, 2, 3, 4, 5], [6, 7, 8, 9]], [[6, 7, 8, 9], [1, 2, 3, 4, 5]]]
faults = ["MemL-Exp", "MemL-Lin", "MemL-Rnd", "PacL-Lin", "PacL-Exp", "PacL-Rnd", "CpuH-Exp", "CpuH-Lin", "CpuH-Rnd"]
data_set_types = ["training-data", "test-data"]

# TODO: to recall why n8a_1__eX_04.txt anomalies used in premise instead of n8a_1__eX_1.txt)

# **** Functions

def get_kpi_list(_kpi_list_file_path):
    _fil = open(_kpi_list_file_path, 'r')
    _reader = csv.reader(_fil)
    _header = next(_reader, None)

    return _header


def get_pair_id_by_node_name(node_name, cluster_node_pairs):

    result_node_pair_id = -1

    for node_pair_id in range(len(cluster_node_pairs)):
        if node_name in cluster_node_pairs[node_pair_id]:
            result_node_pair_id = node_pair_id

    if result_node_pair_id == -1:
        print("Node ", node_name, " does not exist in the KPI List")
        exit(1)

    return result_node_pair_id


def create_folder(folder_path):
    if not os.path.exists(folder_path):
        try:
            os.mkdir(folder_path)
        except OSError:
            print("Creation of the directory %s failed" % folder_path)
            exit(1)


def gen_exp_unique_code(p_exp_unique_code):
    unique_code_str = ""

    for zz in range(10 - len(str(p_exp_unique_code))):
        unique_code_str += "0"

    return unique_code_str + str(p_exp_unique_code)


# **** Run

kpi_list = get_kpi_list(kpi_list_file_path)

cluster_node_pairs = str(configuration['nodes']['pairs']).split(", ")
for ii in range(len(cluster_node_pairs)):
    cluster_node_pairs[ii] = cluster_node_pairs[ii].split(" ")

# Loop by models [0, 1]
for model in range(len(fault_code_list)):
    create_folder(root_folder + "Toolset-Premise/data/anomalies-{model}".format(model=model))

    exp_unique_code = -1

    # Loop by data-sets [0 - training, 1 - test]
    for data_set_type in range(len(fault_code_list[model])):
        create_folder(root_folder + "Toolset-Premise/data/anomalies-{model}/{data_set_type}".format(model=model, data_set_type=data_set_types[data_set_type]))

        # Loop by fault types
        faulty_codes_counter = 0
        for fault_code in fault_code_list[model][data_set_type]:
            faulty_codes_counter += 1

            experiment_data_set_code = "e" + str(fault_code)
            print(experiment_data_set_code)

            start_time = data_sets_configuration['data_sets'][experiment_data_set_code]["start_time"]
            fault_injection_time = data_sets_configuration['data_sets'][experiment_data_set_code]["fault_injection_time"]
            failure_time = data_sets_configuration['data_sets'][experiment_data_set_code]["failure_time"]
            end_time = data_sets_configuration['data_sets'][experiment_data_set_code]["end_time"]

            start_time = datetime.strptime(start_time, '%Y.%m.%d.%H.%M')
            fault_injection_time = datetime.strptime(fault_injection_time, '%Y.%m.%d.%H.%M')
            failure_time = datetime.strptime(failure_time, '%Y.%m.%d.%H.%M')
            end_time = datetime.strptime(end_time, '%Y.%m.%d.%H.%M')

            start_timestamp = utils.datetime_timestamp_utc(start_time)
            fault_injection_timestamp = utils.datetime_timestamp_utc(fault_injection_time)
            failure_timestamp = utils.datetime_timestamp_utc(failure_time)
            end_timestamp = utils.datetime_timestamp_utc(end_time)

            print("fault_injection_timestamp: " + str(utils.timestamp_to_datetime_utc(fault_injection_timestamp)))
            print("fault_injection minute: ", (fault_injection_timestamp - start_timestamp) / 60 + 1)
            print("faulty period duration: ", (failure_timestamp - fault_injection_timestamp)/60)
            print("normal period duration: ", (fault_injection_timestamp - start_timestamp) / 60)

            # Loop by node pairs [0, 1, .., 9]
            for pair_id in pair_id_list:

                # only pair 0 for testing purposes
                if data_set_type == 1 and pair_id != 0:
                    continue

                anomalies_file_path = anomalies_file_path_pattern.format(fault_code=fault_code, pair_id=pair_id)

                fault_type = faults[fault_code-1].split("-")[0]
                fault_pattern = faults[fault_code-1].split("-")[1]

                # normal data for one type of injection experiment only (and only for training purposes)
                if data_set_type == 0:
                    if faulty_codes_counter == 1:
                        exp_unique_code += 1
                        exp_id = gen_exp_unique_code(exp_unique_code)

                        premise_exp_folder_path_normal = premise_exp_folder_path_pattern_normal.format(model=model, data_set_type=data_set_types[data_set_type], id=exp_id)
                        create_folder(premise_exp_folder_path_normal)

                exp_unique_code += 1
                exp_id = gen_exp_unique_code(exp_unique_code)

                premise_exp_folder_path_faulty = premise_exp_folder_path_pattern_faulty.format(model=model, data_set_type=data_set_types[data_set_type], id=exp_id, fault_type=fault_type, faulty_pair_id=pair_id, fault_pattern=fault_pattern)
                create_folder(premise_exp_folder_path_faulty)

                f = open(anomalies_file_path, 'r')
                reader = csv.reader(f)
                header = next(reader, None)

                ii = -1
                # Loop by rows in the experiment file
                for row in reader:
                    ii += 1
                    timestamp = int(row[0])

                    if data_set_type == 0:
                        if timestamp >= fault_injection_timestamp:
                            premise_exp_folder_path = premise_exp_folder_path_faulty
                        else:
                            # normal data for one type of injection experiment only (and only for training purposes)
                            if faulty_codes_counter == 1:
                                premise_exp_folder_path = premise_exp_folder_path_normal
                            else:
                                continue
                    else:
                        premise_exp_folder_path = premise_exp_folder_path_faulty

                    premise_exp_file_path = os.path.join(premise_exp_folder_path, premise_exp_file_name_pattern.format(minute_of_experiment=(ii + 1)))

                    records = []
                    for kpi_index in range(len(kpi_list)):
                        cell_value = int(row[kpi_index + 1])
                        if cell_value == 1:
                            kpi = str(kpi_list[kpi_index])
                            node_name = kpi.split("_")[0]
                            node_pair_id = get_pair_id_by_node_name(node_name, cluster_node_pairs)
                            records.append(premise_exp_file_row_pattern.format(pair_id=node_pair_id, metric=kpi))

                    with open(premise_exp_file_path, "a") as file_object:
                        for record in records:
                            file_object.write(record)
