# -*- coding: utf-8 -*-
"""The module that contains the supercalss of anomaly ranker.
"""
from abc import abstractmethod
import util.causality_graph as causality_graph
import numpy as np


class GeneralRanker(object):
    """Abstract superclass of ranking algorithms.

    Any adoption of ranking algorithms should inherit this class, and implement
    rank() class method and predict() class method.
    """
    @classmethod
    @abstractmethod
    def rank(cls, anomalies_seq):
        """Abstract ranking class method.

        Classes inherit this class should implement this method, which is
        supposed to contain the user's stratagy of ranking the anomalies.

        Args:
            anomalies_seq(list): A list of sets, each set contains the
                anomalies' idices at a timestamp.

        Returns:
            A list whose elements are the anomaly list. Each anoamly list
            contains the tuples of KPI index and rankings. Example: [[${KPI
            index 1}, ${KPI ranking 1}, ${KPI index 2}, ${KPI ranking 2}, ...],
            ...]
        """
        pass

    @classmethod
    def sub_matrix(cls, anomaly_list):
        """Helper class method to get a adjecency matrix of the anomalies.

        Args:
            anomaly_list(list): The list that contains the anomalies' idices at
                a timestamp.

        Returns:
            An adjecency matrix that represents the sub-graph in the causality
            graph which only contains the anomalies.
        """

        full_matrix = causality_graph.get_weighted_matrix()

        # print("\nGeneralRanker. Full matrix (from saved file):\n")
        # for item in full_matrix:
        #     print(item)
        # print("\nGeneralRanker. Anomaly list: ", anomaly_list)

        sub_matrix = []
        len_submx = len(anomaly_list)

        for i in range(len_submx):
            row = []
            for j in range(len_submx):
                if anomaly_list[i] is not -1 and anomaly_list[j] is not -1:
                    row.append(full_matrix[anomaly_list[i]][anomaly_list[j]])
                else:
                    row.append(0)
            sub_matrix.append(row)

        return np.matrix(sub_matrix)
