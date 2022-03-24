import csv
import json
import os
from typing import List
from h2o import h2o, estimators
from h2o.estimators import H2OAutoEncoderEstimator
import pandas as pd
from itertools import islice
from datetime import datetime, timedelta
from anomaly_detector import AnomalyDetector


def remove_symbols(file_path, symbols_cur, symbols_new):
    fin = open(file_path, "rt")
    data = fin.read()
    data = data.replace(symbols_cur, symbols_new)
    fin.close()

    fin = open(file_path, "wt")
    fin.write(data)
    fin.close()


def check_if_string_in_file(file_name, string_to_search):
    with open(file_name, 'r') as read_obj:
        for line in read_obj:
            if string_to_search in line:
                return True
    return False


# Converts datetime string to datetime.timestamp
# Input example: 2019-12-10T18:09:00.*
# Where * is any number of any symbols
def datetime_to_timestamp(datetime_string):
    tempArr = datetime_string.split(":00.")
    newDateTimeString = tempArr[0]

    tempArr = newDateTimeString.split("T")
    newDateString = tempArr[0]
    newTimeString = tempArr[1]

    tempArr = newDateString.split("-")
    year = int(tempArr[0])
    month = int(tempArr[1])
    day = int(tempArr[2])

    tempArr = newTimeString.split(":")
    hour = int(tempArr[0])
    minute = int(tempArr[1])

    dt = datetime(year, month, day, hour, minute)
    timestamp = int(datetime.timestamp(dt))

    # print("datetime: " + datetime_string + " / " + str(timestamp))

    return timestamp


class AutoEncoder(AnomalyDetector):
    """
    Implement an anomaly detector using an H2O autoencoder.
    """

    model = None
    H2O_RECONSTRUCTION_ERROR_COLUMN_NAME_PATTERN = 'reconstr_{kpi_name_}.SE'

    def __init__(self, model_file_path, training_cache_file_path, validation_cache_file_path, log_file_path, configuration_file_path: str, work_directory_path: str = None):
        super().__init__(training_cache_file_path, validation_cache_file_path, log_file_path, configuration_file_path, work_directory_path)
        self._model_file_path: str = model_file_path

    def populate(self, data_file_path, records_num, cache_file_path):

        # Create cache
        # Read the file as a slice, extract the data from the slice as json records, transform the json records to
        # data frames, append the data frames to the cache data frames

        cache_df = pd.DataFrame()
        for record_json in self._get_records_slice(records_num, 0, data_file_path):
            record_df = self._convert_record_json_to_dataframe(record_json)
            cache_df = cache_df.append(record_df, ignore_index=True)

        # Save cache to the disc
        cache_df.to_hdf(cache_file_path, 'data', format='table')

    def train(self) -> None:

        self._connect_h2o()
        self._clean_h2o()

        # Read the Populated Cache
        training_df = self._load_cache("training")
        validation_df = self._load_cache("validation")

        # Load the Populated Cache as a Training H2O Data frame
        training_h2o = h2o.H2OFrame(training_df)
        validation_h2o = h2o.H2OFrame(validation_df)

        checkpoint_model_id = None
        epochs = self._configuration['h2o']['autoencoder']['epochs']

        # Create the Model
        self.model = H2OAutoEncoderEstimator(
            activation=self._configuration['h2o']['autoencoder']['activation_function'],
            autoencoder=True,
            checkpoint=checkpoint_model_id,
            epochs=epochs,
            hidden=self._create_hidden_layers(training_df),
            ignore_const_cols=True,
            ignored_columns=['timestamp'],
            l1=self._configuration['h2o']['autoencoder']['l1'],
            max_w2=self._configuration['h2o']['autoencoder']['max_w2'],
            score_each_iteration=self._configuration['h2o']['autoencoder']['score_each_iteration'],
            sparse=self._configuration['h2o']['autoencoder']['sparse'],
            stopping_rounds=0
        )

        # Train (or re-train) the Model using the Training Data frame (created from the Populated Cache)
        self.model.train(training_frame=training_h2o, validation_frame=validation_h2o)

        # Store the trained Model w/o using temp file
        model_file_path = h2o.save_model(self.model, "resources/output", force=True)
        os.rename(model_file_path, self._model_file_path)

    def detect_batch(self, data_file_path, records_num, output_file_path):

        self.connect_h2o()
        self._clean_h2o()

        model = self._load_model()

        anomalies = []

        the_slice = self._get_records_slice(records_num, 0, data_file_path)

        for jj in range(records_num):

            # Retrieve a record from the slice
            record_json = next(the_slice)

            # Convert the record to the data frame
            record_df = self._autoencoder._convert_record_json_to_dataframe(record_json)

            # Detect anomalous key-value pairs for a given record
            anomalous_kpis_json = json.loads(self._autoencoder.detect(model, record_df))

            # Append an anomalies to the JSON data structure
            anomalies.append(anomalous_kpis_json)

            with open(output_file_path, "w") as outfile:
                json.dump(anomalies, outfile)
                outfile.close()

            # remove extra brackets
            symbols_curs = ["][", "]], [["]
            symbols_new = "], ["
            for symbols_cur in symbols_curs:
                if check_if_string_in_file(output_file_path, symbols_cur):
                    remove_symbols(output_file_path, symbols_cur, symbols_new)
                    if not check_if_string_in_file(output_file_path, symbols_cur):
                        self._autoencoder._logger.info(
                            symbols_cur + " symbols replaced by " + symbols_new + " in: " + output_file_path)

    def detect(self, model, record_df, re_thr) -> str:

        # Transform the record data frame to the H2O data frame
        record_h2o = h2o.H2OFrame(record_df)

        # Remove the timestamp column.
        record_h2o = record_h2o.drop('timestamp')

        # Compute the reconstruction error for each values in the given record
        reconstruction_error_df = model.anomaly(record_h2o, per_feature=True).as_data_frame()

        # Compute the reconstruction error for the given record
        # reconstruction_error = model.anomaly(record_h2o, per_feature=False).as_data_frame()
        # self._logger.info("R: " + str(reconstruction_error["Reconstruction.MSE"]))

        # Return the anomalous KPIs
        result = []
        for column_name in record_df:
            if column_name == 'timestamp':
                continue

            # Retrieve the column name for the reconstruction error data frame
            reconstruction_error_column_name = \
                AutoEncoder.H2O_RECONSTRUCTION_ERROR_COLUMN_NAME_PATTERN.format(kpi_name_=column_name)

            # Check if the current KPI is anomalous and save it to the result array if it actually is
            if reconstruction_error_column_name in reconstruction_error_df:

                reconstruction_error = float(reconstruction_error_df[reconstruction_error_column_name])

                if reconstruction_error >= re_thr:
                    result.append(self._create_kpi_dict(
                        timestamp=int(record_df['timestamp']),
                        kpi_name=column_name,
                        value=float(record_df[column_name]),
                    ))

        return json.dumps(result)

    def show_scoring_history(self):
        self._connect_h2o()
        l_model = self._load_model()
        print(l_model.scoring_history())

    def delete_model(self):
        self._delete_model()

    def delete_cache(self):
        self._delete_cache()

    # def _load_model(self) -> h2o.H2OAutoEncoderEstimator:
    def _load_model(self) -> estimators.deeplearning.H2OAutoEncoderEstimator:
        print(self._model_file_path)
        return h2o.load_model(self._model_file_path)

    # def _get_epochs(self, model: h2o.H2OAutoEncoderEstimator) -> float:
    def _get_epochs(self, model: estimators.deeplearning.H2OAutoEncoderEstimator) -> float:
        """
        Get the number of epochs for the given model.
        :param h2o.H2OAutoEncoderEstimator model: The model.
        :return: The number of epochs.
        :rtype: float
        """
        return model.get_params()['epochs']['actual_value']

    def _delete_model(self) -> None:
        if os.path.exists(self._model_file_path):
            os.remove(self._model_file_path)

    def _connect_h2o(self) -> None:
        """
        Initialize H2O as a local instance or connect to a remote instance.
        """
        if self._configuration['h2o']['local']:
            h2o.init()
        else:
            h2o.connect(ip=self._configuration['h2o']['hostname'], port=self._configuration['h2o']['port'])

    def _clean_h2o(self) -> None:
        h2o.remove_all()

    @staticmethod
    def _create_hidden_layers(dataframe: pd.DataFrame) -> List[int]:
        """
        Create the hidden layers for the autoencoder.

        :param pd.DataFrame dataframe: The dataframe of training data.
        :return: The configuration for hidden layers.
        :rtype: List[int]
        """
        metrics_num = len(dataframe.columns)
        k_factor = 1 / 3
        first_layer = int(metrics_num * k_factor)
        second_layer = int(first_layer * k_factor)
        third_layer = int(second_layer * k_factor)
        return [first_layer, second_layer, third_layer, second_layer, first_layer]

    # Generate a KPI list
    def generate_kpi_list(self, source_file_path, outcome_file_path):

        # Get the data slice from the data set
        the_slice = self._get_records_slice(1, 0, source_file_path)

        the_row = next(the_slice)
        the_row = json.loads(the_row)

        # Create JSON structure
        data = {"kpis": the_row}

        # Save the JSON structure to the file
        with open(outcome_file_path, 'w') as outfile:
            json.dump(data, outfile)

    # iteratively return a records from the records set returned by the _records_json_generator function
    def _get_records_slice(self, size, start, file_path):
        return islice(self._records_json_generator(file_path), int(start), int(start) + int(size))

    # Returns all records from the csv_file_path in json format excluding the title record
    @staticmethod
    def _records_json_generator(csv_file_path):

        with open(csv_file_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:

                record = []

                timestamp = row['timestamp']
                timestamp = datetime_to_timestamp(timestamp)

                iii = 0
                for key, value in row.items():

                    if key == 'timestamp':
                        continue

                    iii = iii + 1
                    key = "a_" + str(iii)

                    kpi_resource, kpi_metric = key.split("_", 1)

                    record.append({
                        'timestamp': timestamp,
                        'resource': {
                            'name': kpi_resource,
                        },
                        'metric': {
                            'name': kpi_metric,
                        },
                        'value': value,
                    })

                yield json.dumps(record)
