import csv
import json
from itertools import islice
from datetime import datetime, timedelta
import pandas as pd
from autoencoder import AutoEncoder


class MyAutoencoder():

    def setUp(self, is_it_the_first_iteration, model_file_path, cache_file_path, log_file_path, CONFIGURATION_FILE_PATH, THIS_DIRECTORY_PATH):
        self._autoencoder = AutoEncoder(model_file_path, cache_file_path, cache_file_path, log_file_path, CONFIGURATION_FILE_PATH, THIS_DIRECTORY_PATH)

        if is_it_the_first_iteration == "Y":
            self._autoencoder.reset()

    def populate_and_train(self, input_dir, start_datetime, end_datetime, time_delta):

        self._autoencoder._connect_h2o()
        self._autoencoder._clean_h2o()

        cache_df = pd.DataFrame()

        ii = 0
        training_iteration = 0
        first_iteration = True
        while True:

            if first_iteration:
                datetimeFrom = start_datetime
                first_iteration = False
            else:
                datetimeFrom = datetimeFrom + timedelta(minutes=time_delta)

            datetimeTo = datetimeFrom + timedelta(minutes=time_delta)

            if datetimeFrom >= end_datetime:
                break

            file_path = input_dir + "data_" + "combined" + "_" + str(
                datetimeFrom.strftime("%Y-%m-%dT%H:%M:%S%z.000")) + "_" + str(
                datetimeTo.strftime("%Y-%m-%dT%H:%M:%S%z.000") + ".csv")

            # Read the file as a slice, extract the data from the slice as json records, transform the json records to
            # data frames, append the data frames to the cache data frames
            for record_json in self._get_records_slice(time_delta, 0, file_path):
                record_df = self._autoencoder._convert_record_json_to_dataframe(record_json)
                cache_df = cache_df.append(record_df, ignore_index=True)

            ii = ii + 1

            # Cache every 3 hours
            if ii % 6 != 0:
                continue

            # Cache to the disc
            cache_df.to_hdf(self._autoencoder._cache_file_path, 'data', format='table')

            self._autoencoder.train(training_iteration)
            training_iteration = training_iteration + 1

            # Create new data frame for cache (reset cache)
            cache_df = pd.DataFrame()

            # Remove the stored training data cache
            self._autoencoder.reset_cache()

    # Detect Anomalies and stores them into file
    def detect(self, input_dir, start_datetime, end_datetime, time_delta, output_file_path, anomalies_set_thr):

        self._autoencoder._connect_h2o()
        self._autoencoder._clean_h2o()

        model = self._autoencoder._load_model()

        anomalies = []

        first_iteration = True
        ii = 0
        # Repeat slice by slice (i.e. file by file)
        while True:

            if first_iteration:
                datetimeFrom = start_datetime
                first_iteration = False
            else:
                datetimeFrom = datetimeFrom + timedelta(minutes=time_delta)

            datetimeTo = datetimeFrom + timedelta(minutes=time_delta)

            if datetimeFrom >= end_datetime:
                # Cache if this is the and and there were odd count of files in total
                if ii % 2 != 0:
                    with open(output_file_path, 'a+') as outfile:
                        json.dump(anomalies, outfile)
                        outfile.close()
                break

            file_path = input_dir + "data_" + "combined" + "_" + str(
                datetimeFrom.strftime("%Y-%m-%dT%H:%M:%S%z.000")) + "_" + str(
                datetimeTo.strftime("%Y-%m-%dT%H:%M:%S%z.000") + ".csv")

            the_slice = self._get_records_slice(time_delta, 0, file_path)

            for jj in range(time_delta):
                self._autoencoder._logger.info("Reading file/row: " + file_path + " : " + str(jj))

                # Retrieve a record from the slice
                record_json = next(the_slice)

                # Convert the record to the data frame
                record_df = self._autoencoder._convert_record_json_to_dataframe(record_json)

                # Detect anomalous key-value pairs for a given record
                anomalous_kpis_json = json.loads(self._autoencoder.detect(model, record_df, anomalies_set_thr))

                # Append an anomalies to the JSON data structure
                anomalies.append(anomalous_kpis_json)

            ii = ii + 1

            # Cache every 1 hours
            if ii % 2 != 0:
                continue

            if ii == 2:
                # first save
                file_open_mode = "w"
            else:
                # consequential saves
                file_open_mode = 'a+'

            with open(output_file_path, file_open_mode) as outfile:
                json.dump(anomalies, outfile)
                outfile.close()

            anomalies.clear()

            self._autoencoder._clean_h2o()
            model = self._autoencoder._load_model()

        # remove extra brackets
        symbols_curs = ["][", "]], [["]
        symbols_new = "], ["
        for symbols_cur in symbols_curs:
            if check_if_string_in_file(output_file_path, symbols_cur):
                remove_symbols(output_file_path, symbols_cur, symbols_new)
                if not check_if_string_in_file(output_file_path, symbols_cur):
                    self._autoencoder._logger.info(symbols_cur + " symbols replaced by " + symbols_new + " in: " + output_file_path)

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

    def show_cache(self):
        self._autoencoder.show_the_cache()

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


def check_if_string_in_file(file_name, string_to_search):
    with open(file_name, 'r') as read_obj:
        for line in read_obj:
            if string_to_search in line:
                return True
    return False


def remove_symbols(file_path, symbols_cur, symbols_new):
    fin = open(file_path, "rt")
    data = fin.read()
    data = data.replace(symbols_cur, symbols_new)
    fin.close()

    fin = open(file_path, "wt")
    fin.write(data)
    fin.close()
