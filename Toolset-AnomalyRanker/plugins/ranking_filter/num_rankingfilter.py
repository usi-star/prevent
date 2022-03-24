# -*- coding: utf-8 -*-
"""The module that contains ranking filter which filter out rankings by the
numer of anomalies.
"""
from plugins.ranking_filter.general_rankingfilter import GeneralRankingFilter
from util.localizer_config import config
from util.kpi_info import kpi_list


class NumRankingFilter(GeneralRankingFilter):
    """This class filters experiment by the number of anomalies.

    If the number of anomalies exceeds some threshold, it will be filter some
    KPIs. The threshold and target KPIs are defined by
    '[ranking_filter]/<num_filter_threshold>' and
    '[ranking_filter]/<num_filter_name>' in the config file.
    """
    @classmethod
    def filter_(cls, exp, ranking_list):
        """Implementation of filter_ method.  See class doc for more
        information.

        Args:
            exp(obj): An util.runtime.Observation instance.
            ranking_list(list): A list which contains a ranking of KPIs
                oraganized in time sereis, i.e.: [[(${KPI index 1}, ${Ranking
                1}), (${KPI index 2}, ${Ranking 2}), ...], ...].

        Returns:
            The new ranking list after filtering.
        """

        num_filter_threshold = config.getint('ranking_filter',
                                             'num_filter_threshold')
        num_filter_name = config.get('ranking_filter',
                                     'num_filter_name')

        new_ranking_list = []
        for ranking in ranking_list:
            if len(ranking) > num_filter_threshold:
                new_ranking_list.append(ranking)
                continue

            filtered_ranking = []
            for idx, val in ranking:
                if num_filter_name not in kpi_list[idx].resource:
                    filtered_ranking.append((idx, val))
            new_ranking_list.append(filtered_ranking)

        return new_ranking_list
