# -*- coding: utf-8 -*-
"""The module that contains the supercalss of ranking filter.
"""
from abc import abstractmethod


class GeneralRankingFilter(object):
    """Abstract superclass of ranking filter.

    Any adoption of ranking filter should inherit this class, and implement
    filter_() class method.
    """
    @classmethod
    @abstractmethod
    def filter_(cls, exp, ranking_list):
        """Abstract filter_ class method.

        Classes inherit this class should implement this method, which is
        supposed to contain the user's stratagy of filtering out the
        rankings.

        Args:
            exp(obj): An util.runtime.Observation instance.
            ranking_list(list): A list which contains a ranking of KPIs
                oraganized in time sereis, i.e.: [[(${KPI index 1}, ${Ranking
                1}), (${KPI index 2}, ${Ranking 2}), ...], ...].

        Returns:
            The new ranking list after filtering.
        """
        pass
