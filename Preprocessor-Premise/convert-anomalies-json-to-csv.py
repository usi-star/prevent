import requests
from datetime import datetime
import utils
import yaml as yaml

# **** Inputs

fp_server_port = 5000
exp_codes = ["e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9"]

# **** Paths

root_folder = "../"
configuration = yaml.load(open(root_folder + "resources/configuration/configuration.yml"), Loader=yaml.FullLoader)
data_sets_configuration = yaml.load(open(root_folder + "resources/configuration/data_sets.yml"), Loader=yaml.FullLoader)

anomalies_file_path_pattern = root_folder + "resources/data/anomalies/{exp_code}.txt"
fp_server_address = 'http://localhost:' + str(fp_server_port)

# ***** Run

for exp_code in exp_codes:

    fault_injection_time = data_sets_configuration['data_sets'][exp_code]["fault_injection_time"]
    failure_time = data_sets_configuration['data_sets'][exp_code]["failure_time"]

    fault_injection_time = datetime.strptime(fault_injection_time, '%Y.%m.%d.%H.%M')
    failure_time = datetime.strptime(failure_time, '%Y.%m.%d.%H.%M')

    fault_injection_timestamp = utils.datetime_timestamp_utc(fault_injection_time)
    failure_timestamp = utils.datetime_timestamp_utc(failure_time)

    print(fault_injection_timestamp, failure_timestamp, exp_code)

    with open(anomalies_file_path_pattern.format(exp_code=exp_code), 'r') as file:
        response = requests.post(fp_server_address + '/convert_anomalies?anomalies_file_name=' + exp_code + '&fault_injection_timestamp=' + str(fault_injection_timestamp) + '&failure_timestamp=' + str(failure_timestamp) + '&fault_class_name=' + exp_code, data=file.read(), headers={"Content-Type": "application/json"})
        print(response.content)
