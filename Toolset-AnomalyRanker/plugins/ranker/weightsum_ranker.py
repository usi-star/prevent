# -*- coding: utf-8 -*-
"""The module that contains anomaly ranker that ranks the anomalies by
summing up the weights of the KPI.
"""
from plugins.ranker.general_ranker import GeneralRanker


class WeightSumRanker(GeneralRanker):
    """This class ranks the anomalies by summing up the weights of the KPI.
    """
    @classmethod
    def rank(cls, anomalies_seq, graph=None):
        """Implementation of rank. See class doc for more information.

        Args:
            anomalies_seq(list): A list of sets, each set contains the
                anomalies' idices at a timestamp.

        Returns:
            A list whose elements are the anomaly list. Each anoamly list
            contains the tuples of KPI index and rankings. Example: [[${KPI
            index 1}, ${KPI ranking 1}, ${KPI index 2}, ${KPI ranking 2}, ...],
            ...]
        """
        if len(anomalies_seq) is 0:
            return [], []

        anomaly_list = sorted(list(anomalies_seq))
        sub_matrix = cls.sub_matrix(anomaly_list)

        id_val_list = []

        for cnt, idx in enumerate(anomaly_list):
            val = sum(sub_matrix[cnt])
            id_val_list.append((idx, val))

        sorted_list = sorted(id_val_list,
                             key=lambda x: float(x[1]),
                             reverse=True)

        rankings = []
        values = []
        for (idx, value) in sorted_list:
            if value <= 0:
                break
            rankings.append(idx)
            values.append(value)

        return rankings, values
