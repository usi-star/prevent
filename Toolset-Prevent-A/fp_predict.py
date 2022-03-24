import json
import os
import sys
import requests
from typing import Dict
import utils

# **** Configuration

script_dir = os.path.dirname(os.path.abspath(__file__))

configuration_file_path = os.path.join(script_dir, 'resources/configuration/configuration.yml')
configuration: Dict = utils.parse_yaml(configuration_file_path)

data_sets_configuration_file_path = os.path.join(script_dir, 'resources/configuration/data_sets.yml')
data_sets_configuration: Dict = utils.parse_yaml(data_sets_configuration_file_path)

# ******************************************************************************************* Inputs

ad_model_code = sys.argv[1]
fp_train_data_set_code = sys.argv[2]
novelties_set_thr = str(sys.argv[3])
nu = str(sys.argv[4])
gamma = str(sys.argv[5])
experiment_data_set_code = sys.argv[6]
anomalies_set_thr = str(sys.argv[7])
fp_server_port = sys.argv[8]

novelties_set_thr, novelties_set_thr_str = utils.get_input_thrs(novelties_set_thr)
nu, nu_str = utils.get_input_thrs(nu)
gamma, gamma_str = utils.get_input_thrs(gamma)
anomalies_set_thr, anomalies_set_thr_str = utils.get_input_thrs(anomalies_set_thr)

# **** Local Configuration

fp_model_code = ad_model_code + "__" + fp_train_data_set_code + "_" + novelties_set_thr_str + "__prm_" + nu_str + "_" + gamma_str
anomalies_file_path = os.path.join(script_dir, configuration['ad']['anomalies_file_path'].format(ad_model_code=ad_model_code, data_set_code=experiment_data_set_code, thr=anomalies_set_thr_str))
predictions_file_path = os.path.join(script_dir, configuration['fp']['predictions_file_path'].format(ad_model_code=ad_model_code, fp_train_data_set_code=fp_train_data_set_code, novelties_set_thr=novelties_set_thr_str, nu=nu_str, gamma=gamma_str, experiment_data_set_code=experiment_data_set_code, anomalies_set_thr=anomalies_set_thr_str))
fp_server_address = 'http://localhost:' + fp_server_port

# ******************************************************************************************* Run

response = requests.get(fp_server_address + '/set_pred_model?model_code=' + fp_model_code)
print(fp_model_code + " model set result: " + str(response.content))

with open(anomalies_file_path, 'r') as json_file:
    anomalies_json = '{"anomalies": ' + json_file.read() + '}'
    anomalies_json = json.loads(anomalies_json)

    predictions = {"predictions": []}

    # Repeat for each timestamp
    for i in range(len(anomalies_json["anomalies"])):

        # Read anomalies for certain timestamp
        data_dmp = {"anomalies": anomalies_json["anomalies"][i]}
        data_dmp = json.dumps(data_dmp)

        print(i, data_dmp)
        input()

        response = requests.post(fp_server_address + '/predict', data=data_dmp, headers={"Content-Type": "application/json"})
        predictions["predictions"].append(json.loads(response.content))

    with open(predictions_file_path, 'w') as outfile:
        json.dump(predictions, outfile)
