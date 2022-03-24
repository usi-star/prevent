import abc
import json
import os
import re
import shutil
import sys
import tempfile
import yaml as yaml

import logbook
import pandas as pd

#import anomalydetector.utils
import utils

THIS_DIRECTORY_PATH = os.path.dirname(os.path.abspath(__file__))


class AnomalyDetector(abc.ABC):
    """
    An anomaly detector uses a cache of stored records to build or update a model for prediction.

    Each record is composed of:
    - a timestamp
    - the list of KPI values
    """

    KPI_NAME_PATTERN = '{metric_}::{resource_}'
    KPI_NAME_REGEX = re.compile(r'(.+)::(.+)')

    def __init__(self, training_cache_file_path, validation_cache_file_path, log_file_path, configuration_file_path: str, work_directory_path: str = None,
                 logger_name: str = 'Anomaly Detector') -> None:
        """
        Initialize the anomaly detector with a configuration.

        :param str configuration_file_path: The path of the YAML configuration file.
        :param str work_directory_path: The path of the root directory for the resources paths indicated into the
        configuration file. Otherwise, use the directory where Python is executed.
        :param logger_name: The name of the logger.
        """

        self._configuration = yaml.load(open(configuration_file_path), Loader=yaml.FullLoader)
        self._work_directory_path: str = work_directory_path if work_directory_path else THIS_DIRECTORY_PATH

        self._cache_file_path1: str = training_cache_file_path
        self._cache_file_path2: str = validation_cache_file_path

        logbook.StreamHandler(sys.stdout).push_application()
        logbook.FileHandler(log_file_path, bubble=True).push_application()
        log_level = logbook.INFO if self._configuration['log']['level'] == 'info' else logbook.DEBUG
        self._logger = logbook.Logger(logger_name, level=log_level)

    # storing into the cash. record_json comes with index titles
    def store(self, data_type, record_json: str) -> None:

        """
        Store the given JSON record into the cache.

        The record is a JSON string in the format::

            [
                {
                    'timestamp': 15227510000,
                    'resource': {
                        'name': 'Node2'
                    },
                    'metric': {
                        'name': 'MEMORY'
                    },
                    'value': 48
                },
                ...
            ]

        :param data_type:
        :param str record_json: A JSON string representing KPIs for a single timestamp.
        """

        if data_type == "training":
            cache_file_path = self._cache_file_path1

        if data_type == "validation":
            cache_file_path = self._cache_file_path2

        # Load the cache data frame, if any.
        if os.path.exists(cache_file_path):
            cache_df = self._load_cache(data_type)
        else:
            cache_df = pd.DataFrame()

        # Create a data frame for the record.
        record_df = self._convert_record_json_to_dataframe(record_json)

        # Append the record.
        cache_df = cache_df.append(record_df, ignore_index=True)

        # Save the cache.
        cache_df.to_hdf(cache_file_path, 'data', format='table')

    @abc.abstractmethod
    def train(self) -> None:
        """
        Use the current cache to build a new model or update an existing one, if any, and empty the records in cache.
        """
        ...

    @abc.abstractmethod
    def detect(self, record_json: str) -> str:
        """
        Use the stored model to predict anomalies for the given record.

        :param str record_json: A JSON string representing KPIs for a single timestamp.
        :return: The list of anomalous KPIs as a JSON string.
        :rtype: str
        """
        ...

    # Remove the stored training data cache and the trained anomaly detection model
    def reset(self) -> None:

        self._delete_cache()
        self._delete_model()

    # Remove the stored training data cache
    def reset_cache(self) -> None:
        self._delete_cache()

    def _load_cache(self, data_type) -> pd.DataFrame:
        """
        Load the cache from the HDF5 file.

        :return: The dataframe of the cache.
        :rtype: pd.DataFrame
        """

        if data_type == "training":
            cache_file_path = self._cache_file_path1

        if data_type == "validation":
            cache_file_path = self._cache_file_path2

        # Copy into a temporary file to ensure thread safeness.
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        shutil.copyfile(cache_file_path, temp_file.name)

        # Read the data from file.
        cache_df: pd.DataFrame = pd.read_hdf(temp_file.name)

        # Remove the temporary file.
        os.remove(temp_file.name)

        # Return the cache dataframe.
        return cache_df

    def _delete_cache(self) -> None:
        """
        Remove the HDF5 file.
        """
        if os.path.exists(self._cache_file_path1):
            os.remove(self._cache_file_path1)

        if os.path.exists(self._cache_file_path2):
            os.remove(self._cache_file_path2)

    @abc.abstractmethod
    def _load_model(self) -> object:
        """
        Load the model in memory.

        :return: The model.
        :rtype: object
        """
        ...

    @abc.abstractmethod
    def _delete_model(self) -> None:
        """
        Clear the stored model.
        """
        ...

    @staticmethod
    def _convert_record_json_to_dataframe(record_json: str) -> pd.DataFrame:
        """
        Convert a record of a JSON string into a dataframe.

        :param str record_json: A JSON string representing KPIs for a single timestamp.
        :return: The dataframe.
        :rtype: pd.DataFrame
        """
        # Convert the JSON string to a Python list of dictionaries.
        record_object = json.loads(record_json)

        # Transform the record object.
        record_transformed = {
            'timestamp': [int(float(record_object[0]['timestamp']))] if len(record_object) > 0 else None
        }
        for kpi in record_object:
            kpi_name = AnomalyDetector.KPI_NAME_PATTERN.format(
                resource_=kpi['resource']['name'], metric_=kpi['metric']['name']
            )
            record_transformed[kpi_name] = [kpi['value']]

        # Return the dataframe built from the transformed record.
        return pd.DataFrame.from_dict(record_transformed)

    @staticmethod
    def _create_kpi_dict(timestamp: float, kpi_name: str, value: float):
        """
        Create a dictionary for the single KPI in the standard format.

        :param float timestamp: The timestamp.
        :param str kpi_name: The KPI name, including the metric and resource names.
        :param float value: The value of the KPI.
        :return: The dict representing the KPI.
        :rtype: Dict
        """
        metric, resource = AnomalyDetector.KPI_NAME_REGEX.match(kpi_name).groups()

        return {
            'timestamp': timestamp,
            'resource': {
                'name': resource,
            },
            'metric': {
                'name': metric,
            },
            'value': value,
        }