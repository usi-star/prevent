import csv
import os
from datetime import datetime
import json
import requests
import pandas as pd

# **** Input
exp_codes = ["e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9", "normal_w3"]
server_port = 5000

# **** Parameters
root_folder = "../"

# Anomaly Ranker server address
server_address = "http://localhost:{server_port}".format(server_port=server_port)

# Path to the CSV file with the list of KPIs
kpi_titles_file = root_folder + "resources/data/kpi-list.csv"

# Path to the .txt file with the anomalies
anomalies_file_path = root_folder + "resources/data/anomalies/{exp_code}.txt"

# Path to the .txt file to save the localisations
localisations_by_nodes = root_folder + "resources/data/loud/localisations-nodes/{exp_code}.csv"

# **** Run

# Set original names for KPIs in Amnomaly Ranker
os.system('python kpi_list_update_original_names.py')

# Load KPI titles from CSV
df_tmp = pd.read_csv(kpi_titles_file, sep=',', header=None)
kpi_titles = df_tmp.values[0]
# print(kpi_titles, kpi_titles.shape)

for exp_code in exp_codes:

	# Load Anomalies (all from start to failure)
	with open(anomalies_file_path.format(exp_code=exp_code), 'r') as json_file:
		anomalies_json = json.loads(json_file.read())

	with open(localisations_by_nodes.format(exp_code=exp_code), "w") as file_out:
		localisations_writer = csv.writer(file_out)

		# Read anomalies (point by point), send them to the AnomalyRanker, format and write response to the output file
		for i in range(len(anomalies_json)):

			timestamp_obj = datetime.fromtimestamp(anomalies_json[i][0]["timestamp"])
			timestamp = str(timestamp_obj.year) + "-" + str(timestamp_obj.month) + "-" + str(
			timestamp_obj.day) + "T" + str(timestamp_obj.hour) + ":" + str(timestamp_obj.minute) + ":00.000Z"

			for jj in range(len(anomalies_json[i])):
				kpi_index = int(anomalies_json[i][jj]["metric"]["name"])
				kpi_index_in_titles_arr = kpi_index - 1

				node = kpi_titles[kpi_index_in_titles_arr].split("_", 1)[0]
				metric = kpi_titles[kpi_index_in_titles_arr].split("_", 1)[1]

				anomalies_json[i][jj]["resource"]["name"] = node
				anomalies_json[i][jj]["metric"]["name"] = metric

				# print(kpi_index, kpi_index_in_titles_arr, node, metric)

			data = {"anomalies": anomalies_json[i]}

			# Rank KPIs and localise the faulty/suspected nodes
			response = requests.post(server_address + '/localize?rank_selection=325', json=data,
									 headers={"Content-Type": "application/json"})
			response_content_decoded = json.loads(response.content)

			print(exp_code, response_content_decoded)

			# localization_row = response_content_decoded["localization"]
			localization_row = [timestamp, response_content_decoded["localization"]]

			for item in response_content_decoded["suspected_list"]:
				localization_row.append(item[0])
				localization_row.append(item[1])

			localisations_writer.writerow(localization_row)
