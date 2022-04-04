import csv
import pandas as pd
from shutil import copyfile
import yaml as yaml

# **** Inputs

exp_codes = ["e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9"]

# **** Functions

# kpi => recourse
def get_recourse_from_kpi(kpi_):
    kpi_components_list_ = kpi_.split("_")
    recourse_ = kpi_components_list_[0]

    return recourse_


# kpi => metric
def get_metric_from_kpi(kpi_):
    kpi_components_list_ = kpi_.split("_")
    metric_ = "_".join(kpi_components_list_[1:])

    return metric_


# kpi, new_recourse -> new_kpi
def change_recourse_in_kpi(kpi_, new_recourse_):
    metric_ = get_metric_from_kpi(kpi_)
    new_kpi_ = new_recourse_ + "_" + metric_

    return new_kpi_


# **** Configuration

root_folder = "../"
configuration = yaml.load(open(root_folder + "resources/configuration/configuration.yml"), Loader=yaml.FullLoader)
data_sets_configuration = yaml.load(open(root_folder + "resources/configuration/data_sets.yml"), Loader=yaml.FullLoader)

anomalies_file_path_pattern = root_folder + "resources/data/premise/anomalies/{exp_code}.csv"
anomalies_shuffled_file_path_pattern = root_folder + "resources/data/premise/anomalies-shuffled/{exp_code}-{cluster_node_pair_number}.csv"

# ***** Run

cluster_node_pairs = str(configuration['nodes']['pairs']).split(", ")
for ii in range(len(cluster_node_pairs)):
    cluster_node_pairs[ii] = cluster_node_pairs[ii].split(" ")

faulty_node_0 = cluster_node_pairs[0][0]
faulty_node_1 = cluster_node_pairs[0][1]

# ***** Local Configuration

for exp_code in exp_codes:
    anomalies_file_path = anomalies_file_path_pattern.format(exp_code=exp_code)

    for jj in range(0, len(cluster_node_pairs)):

        anomalies_shuffled_file_path = anomalies_shuffled_file_path_pattern.format(exp_code=exp_code, cluster_node_pair_number=str(jj))

        if jj == 0:
            copyfile(anomalies_file_path, anomalies_shuffled_file_path)
            continue

        target_node_0 = cluster_node_pairs[jj][0]
        target_node_1 = cluster_node_pairs[jj][1]

        f = open(anomalies_file_path, 'r')
        reader = csv.reader(f)
        header = next(reader, None)

        header_original = []
        for item in header:
            header_original.append(item)

        with open(anomalies_shuffled_file_path, 'w') as outfile:
            writer = csv.writer(outfile)

            for zz in range(len(header_original)):

                kpi = header_original[zz]
                recourse = get_recourse_from_kpi(kpi)

                if recourse == target_node_0:
                    kpi = change_recourse_in_kpi(kpi, faulty_node_0)
                    pass

                if recourse == target_node_1:
                    kpi = change_recourse_in_kpi(kpi, faulty_node_1)
                    pass

                if recourse == faulty_node_0:
                    kpi = change_recourse_in_kpi(kpi, target_node_0)
                    pass

                if recourse == faulty_node_1:
                    kpi = change_recourse_in_kpi(kpi, target_node_1)
                    pass

                header[zz] = kpi

            writer.writerow(header)
            for row in reader:
                writer.writerow(row)

        f = open(anomalies_shuffled_file_path, 'r')
        reader = csv.reader(f)

        matrix = []
        ff = 0
        for row in reader:
            if ff > 0:
                matrix.append(row)
            else:
                the_header = row
            ff += 1

        pdf = pd.DataFrame(matrix)
        pdf.columns = the_header

        pdf_new = pd.DataFrame()
        for kpi in header_original:
            pdf_new[kpi] = pdf[kpi]

        pdf_new.to_csv(anomalies_shuffled_file_path, index=False)
