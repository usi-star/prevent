import csv
import json
import requests

# **** Inputs
exp_codes = ["e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9", "normal_w3"]
exp_codes = ["normal_w3"]
fp_server_port = 5000

# **** Parameters
root_folder = "../"

anomalies_file_path_pattern = root_folder + "resources/data/anomalies/{exp_code}.txt"
predictions_file_path_pattern = root_folder + "resources/data/prevent-a/predictions/{exp_code}.csv"

fp_model_code = "n8a_1__n8b_04__prm_01_scale"
fp_server_address = 'http://localhost:' + str(fp_server_port)

# **** Run

# set fp model
response = requests.get(fp_server_address + '/set_pred_model?model_code=' + fp_model_code)
print(str(response.content))

for exp_code in exp_codes:
    with open(anomalies_file_path_pattern.format(exp_code=exp_code), 'r') as json_file:
        print(exp_code)

        anomalies_json = '{"anomalies": ' + json_file.read() + '}'
        anomalies_json = json.loads(anomalies_json)

        predictions_writer = csv.writer(open(predictions_file_path_pattern.format(exp_code=exp_code), 'w'))

        prediction_values_history = []
        # Repeat for each timestamp
        for i in range(len(anomalies_json["anomalies"])):

            # Read anomalies for certain timestamp
            data_dmp = {"anomalies": anomalies_json["anomalies"][i]}
            data_dmp = json.dumps(data_dmp)

            response = requests.post(fp_server_address + '/predict', data=data_dmp, headers={"Content-Type": "application/json"})
            prediction_json = json.loads(response.content)
            prediction = int(prediction_json["prediction"])

            prediction_values_history.append(prediction)
            prediction = int((sum(prediction_values_history[-3:]) > 1))

            predictions_writer.writerow([prediction])
