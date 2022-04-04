import sys
import utils
from myAutoencoderClass import MyAutoencoder
import yaml as yaml


# **** Input
prediction_mode = sys.argv[1]

if prediction_mode == "normal_w2":
	exp_codes = ["normal_w2"]
	anomalies_set_thr = "0.4"

if prediction_mode == "normal_w3":
	exp_codes = ["normal_w3"]
	anomalies_set_thr = "0.4"

if prediction_mode == "anomalous":
	exp_codes = ["e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9"]
	anomalies_set_thr = "1"

anomalies_set_thr, anomalies_set_thr_str = utils.get_input_thrs(anomalies_set_thr)


# **** Parameters
root_folder = "../"
configuration_file_path = root_folder + 'resources/configuration/configuration.yml'
configuration = yaml.load(open(configuration_file_path), Loader=yaml.FullLoader)
data_sets_configuration = yaml.load(open(root_folder + "resources/configuration/data_sets.yml"), Loader=yaml.FullLoader)

log_file_path = root_folder + "resources/logs/anomaly_detection.txt"
model_file_path = root_folder + "resources/models/n8a_1.h2o"

input_data_set_dir_templ = root_folder + "resources/data/Datasets-Raw-Splitted/{exp_code}/"
output_anomalies_file_path_templ = root_folder + "resources/data/anomalies/{exp_code}.txt"


for exp_code in exp_codes:

	input_data_set_dir = input_data_set_dir_templ.format(exp_code=exp_code)
	output_anomalies_file_path = output_anomalies_file_path_templ.format(exp_code=exp_code)

	start_time = data_sets_configuration['data_sets'][exp_code]['start_time']
	end_time = data_sets_configuration['data_sets'][exp_code]['end_time']
	time_delta = data_sets_configuration['data_sets'][exp_code]['time_delta']
	start_datetime, end_datetime, time_delta = utils.get_time_range_and_delta(start_time, end_time, time_delta)

	# **** Run
	AnomalyDetector = MyAutoencoder()
	AnomalyDetector.setUp("N", model_file_path, None, log_file_path, configuration_file_path, "")
	AnomalyDetector.detect(input_data_set_dir, start_datetime, end_datetime, time_delta, output_anomalies_file_path, anomalies_set_thr)