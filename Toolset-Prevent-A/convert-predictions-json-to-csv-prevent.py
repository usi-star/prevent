import csv
import json

# exp_codes = ["e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9", "normal_w3"]
exp_codes = ["e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9", "normal_w3"]

root_folder = "../"
json_predictions_file_path = root_folder + "resources/data/prevent-a/predictions/{exp_code}.txt"
csv_predictions_file_path = root_folder + "resources/data/prevent-a/predictions/{exp_code}.csv"

for exp_code in exp_codes:
    with open(json_predictions_file_path.format(exp_code=exp_code), 'r') as json_file:
        predictions_json = json.loads(json_file.read())
        predictions = predictions_json["predictions"]

    predictions_writer = csv.writer(open(csv_predictions_file_path.format(exp_code=exp_code), 'w'))

    for prediction_dict in predictions:
        predictions_writer.writerow([int(prediction_dict["prediction"])])
