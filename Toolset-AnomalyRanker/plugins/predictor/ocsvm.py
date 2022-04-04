# -*- coding: utf-8 -*-
"""The module that contains the class of  one class SVM predictor.
"""
from plugins.predictor.general_predictor import GeneralPredictor
from sklearn import svm


class OneClassSVM(GeneralPredictor):
    """This class uses one class SVM as the predictor.

    The implementation is taken from the sci-kit learn library. Only data from
    normal executions should be provided as the training set.
    """
    predictor = svm.OneClassSVM(nu=0.01, kernel="rbf", gamma=0.1)

    @classmethod
    def train_impl(cls, data, labels):
        """Impementation of train_impl class method.

        Args:
            data(list): A list contains a series of value list for training.
            labels(list): A list of boolean labels that represents the labels
                of the training data. The length of this list should be as long
                as the length of data.

        Returns:
            None
        """
        print("cls.predictor.fit")
        cls.predictor.fit(data)

    @classmethod
    def predict(cls, data):
        """Implementation of predict class method.

        Args:
            data(list): A list contains a series of value list for prediction.

        Returns:
            A list of boolean corresponding to the input dat, where True
            indicates a prediction.
        """
        result = cls.predictor.predict(data)
        return [False if x == 1 else True for x in result]

    @classmethod
    def info(cls):
        """Log the information of some prediction coefficient.

        Args:
            None

        Returns: 
            The string containing some related info of the predictor.
        """
        str_lst = []
        str_lst.append(str(cls.predictor.dual_coef_))
        str_lst.append("Length: %s" % str(len(cls.predictor.dual_coef_[0])))

        return '\n'.join(str_lst)
