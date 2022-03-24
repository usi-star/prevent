import csv
import json
import requests


# **** Input
# test_data_set_codes = ["e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9", "normal_w3"]
test_data_set_codes = ["e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9"]
server_port = 5000
rank_selection = 325


# **** Functions
def get_kpi_list(_kpi_list_file_path):
    _fil = open(_kpi_list_file_path, 'r')
    _reader = csv.reader(_fil)
    _header = next(_reader, None)

    return _header


# **** Parameters
# Anomaly Ranker server address
server_address = "http://localhost:{server_port}"
# Path to the .txt file with the anomalies
anomalies_file_path = "../Data/anomalies/{data_set_code}.txt"
# Path to the .txt file to save the localisations
localisations_file_path = "../Data/localisations/{data_set_code}.csv"
kpi_list_file_path = "../Data/kpi-list.csv"

# **** Initialisation
# Anomaly Ranker server address
server_address = server_address.format(server_port=server_port)
# Data set Configuration
data_sets_config = {"normal_w3": [0, 0, 0],
                    "e1": [150, 92, 126], "e2": [300, 110, 297], "e3": [120, 67, 107],
                    "e4": [120, 32, 105], "e5": [90, 55, 69], "e6": [150, 57, 132],
                    "e7": [60, 34, 49], "e8": [150, 43, 140], "e9": [120, 56, 97]}

# get KPI list
kpi_list = get_kpi_list(kpi_list_file_path)

for test_data_set_code in test_data_set_codes:
    # Load Anomalies (all from start to failure)
    with open(anomalies_file_path.format(data_set_code=test_data_set_code), 'r') as json_file:
        anomalous_kpis_json = json.loads(json_file.read())

    with open(localisations_file_path.format(data_set_code=test_data_set_code), "w") as file_out:
        localisations_writer = csv.writer(file_out)

        # Read anomalies (point by point), send them to the AnomalyRanker, format and write response to the output file
        for i in range(len(anomalous_kpis_json)):

            data = {"anomalies": anomalous_kpis_json[i]}

            # Rank KPIs and localise the faulty/suspected nodes
            response = requests.post(server_address + '/localize?rank_selection=' + str(rank_selection), json=data, headers={"Content-Type": "application/json"})
            response_content_decoded = json.loads(response.content)

            # localization_row = response_content_decoded["localization"]
            localization_row = [str(i), response_content_decoded["localization"]]

            for item in response_content_decoded["suspected_list"]:
                localization_row.append(item[0])
                localization_row.append(item[1])

            localisations_writer.writerow(localization_row)