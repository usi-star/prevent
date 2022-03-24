import csv
import json
import os
import sys

src = sys.argv[1]
dst = sys.argv[2]
ma_period = int(sys.argv[3])
ma_number = int(sys.argv[4])

script_dir = os.path.dirname(os.path.abspath(__file__))
src_file_path = os.path.join(script_dir, "resources/data/NORMAL/19-preface-normal_data/preface-normal_predictions_ma_2_3_json/{src}".format(src=src))
dst_file_path = os.path.join(script_dir, "resources/data/NORMAL/19-preface-normal_data/preface-normal_predictions_ma_2_3/{dst}".format(dst=dst))


def get_ma_prediction(predictions, current_time_point, ma_period, ma_number):

    if predictions[current_time_point] == 0:
        return 0

    ma_sum = 0
    for ii in range(ma_period):
        ma_sum += predictions[current_time_point - ii]

    if ma_sum >= ma_number:
        return 1
    else:
        return 0


file_handler = open(src_file_path, 'r')
reader = csv.reader(file_handler)

with open(src_file_path, 'r') as json_file:
    predictions_json = json.loads(json_file.read())

predictions = [1 if prediction["prediction"] is True else 0 for prediction in predictions_json["predictions"]]
predictions_ma = [get_ma_prediction(predictions, ii, ma_period, ma_number) if ii >= ma_period - 1 else 0 for ii in range(len(predictions))]

# for ii in range(len(predictions_ma)):
#    print(ii, predictions_json["predictions"][ii]["prediction"], predictions_ma[ii])

with open(dst_file_path, "a") as file_out:
    writer = csv.writer(file_out)
    for prediction_ma in predictions_ma:
        writer.writerows([[prediction_ma]])
