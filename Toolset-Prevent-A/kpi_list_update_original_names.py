import json
import requests
import pandas as pd

# **** Input
server_port = 5000

# **** Parameters
root_folder = "../"

# Anomaly Ranker server address
server_address = "http://localhost:{server_port}".format(server_port=server_port)

# Path to the CSV file with the list of KPIs
kpi_titles_file = root_folder + "resources/data/kpi-list.csv"


# **** Run

# Load KPI titles from CSV
df_tmp = pd.read_csv(kpi_titles_file, sep=',', header=None)
kpi_titles = df_tmp.values[0]

kpi_list = []
for ii in range(len(kpi_titles)):
	feature_components_list = kpi_titles[ii].split("_")
	node = feature_components_list[0]
	metric = "_".join(feature_components_list[1:])
	timestamp = "1522751098000"  # fake value
	value = 0  # fake value

	kpi_list.append({
		'timestamp': timestamp,
		'resource': {
			'name': node,
		},
		'metric': {
			'name': metric,
		},
		'value': value,
	})

# Update the Ranker's KPI list
response = requests.post(server_address + "/update_kpi", data=json.dumps({"kpis": kpi_list}), headers={"Content-Type": "application/json"})

print("Ranker: Update KPI list: " + str(response.content))