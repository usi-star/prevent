# -*- coding: utf-8 -*-
"""The module that contains the supercalss of the predictors.
"""
from abc import abstractmethod
import util.localizer_log as localizer_log


class GeneralPredictor(object):
    """Abstract superclass of predictor.

    Any adoption of predictor should inherit this class, and implement
    train_impl() class method and predict() class method.
    """
    @classmethod
    def train(cls, data, labels):
        """Training api of predictor.

        The method will firstly validate the input format, and calls train_impl
        to train on the training data.

        Args:
            data(list): A list contains a series of value list for training.
            labels(list): A list of boolean labels that represents the labels
                of the training data. The length of this list should be as long
                as the length of data.

        Returns:
            None
        """
        if not len(data) == len(labels):
            localizer_log.error(("Length of training data ({len1})"
                                 " not matching length of labels ({len2})")
                                .format(len1=len(data), len2=len(labels)))
        if len(data) < 1:
            localizer_log.error(("Length of training data ({len1})"
                                 " should be at least 1.")
                                .format(len1=len(data)))
        cls.train_impl(data, labels)

    @classmethod
    @abstractmethod
    def train_impl(cls, data, labels):
        """Abstract train_impl class method.

        Classes inherit this class should implement this method, which is
        supposed to train on the training data.

        Args:
            data(list): A list contains a series of value list for training.
            labels(list): A list of boolean labels that represents the labels
                of the training data. The length of this list should be as long
                as the length of data.

        Returns:
            None
        """
        pass

    @classmethod
    @abstractmethod
    def predict(cls, data):
        """Abstract check predict class method.

        Classes inherit this class should implement this method, which is
        supposed to give the prediction on the input data.

        Args:
            data(list): A list contains a series of value list for prediction.

        Returns:
            A list of boolean corresponding to the input dat, where True
            indicates a prediction.
        """
        pass
