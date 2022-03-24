import os
import sys
import requests

from datetime import datetime

import utils

from ruamel.yaml import YAML
from typing import Dict

# ******************************************************************************************* Configuration

script_dir = os.path.dirname(os.path.abspath(__file__))

data_sets_configuration_file_path = os.path.join(script_dir, 'resources/configuration/data_sets.yml')
data_sets_configuration: Dict = utils.parse_yaml(data_sets_configuration_file_path)

input_files_dir = "resources/data/1-anomalies-in-json/"

# ******************************************************************************************* Inputs

anomalies_file_name = str(sys.argv[1])
experiment_data_set_code = str(sys.argv[2])

# ****************************************************************************************** Data set Configuration

fault_injection_time = data_sets_configuration['data_sets'][experiment_data_set_code]["fault_injection_time"]
failure_time = data_sets_configuration['data_sets'][experiment_data_set_code]["failure_time"]

fault_injection_time = datetime.strptime(fault_injection_time, '%Y.%m.%d.%H.%M')
failure_time = datetime.strptime(failure_time, '%Y.%m.%d.%H.%M')

fault_injection_timestamp = utils.datetime_timestamp_utc(fault_injection_time)
failure_timestamp = utils.datetime_timestamp_utc(failure_time)

# ******************************************************************************************* Local Configuration

anomalies_file_path_json = os.path.join(script_dir, input_files_dir + anomalies_file_name)

fp_server_port = 5000
fp_server_address = 'http://localhost:' + str(fp_server_port)

# ******************************************************************************************* Run

fault_injection_timestamp = fault_injection_timestamp
failure_timestamp = failure_timestamp
fault_class_name = experiment_data_set_code

print(fault_injection_timestamp, failure_timestamp, fault_class_name)

with open(anomalies_file_path_json, 'r') as file:
    response = requests.post(fp_server_address + '/convert_anomalies?anomalies_file_name=' + anomalies_file_name + '&fault_injection_timestamp=' + str(fault_injection_timestamp) + '&failure_timestamp=' + str(failure_timestamp) + '&fault_class_name=' + fault_class_name, data=file.read(), headers={"Content-Type": "application/json"})
    print(response.content)
