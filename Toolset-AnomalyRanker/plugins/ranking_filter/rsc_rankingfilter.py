# -*- coding: utf-8 -*-
"""The module that contains ranking filter which filter out rankings by some
resources.
"""
from plugins.ranking_filter.general_rankingfilter import GeneralRankingFilter
from util.localizer_config import config
from util.kpi_info import kpi_list


class RscRankingFilter(GeneralRankingFilter):
    """This class filters rankings by resource pattern in the KPIs.

    Only when the name of the anomalous KPI contains the resource pattern in
    its resource part, it will be processed. This resource pattern is defined
    by '[ranking_filter]/<rsc_filter_name>' in the config file. If the pattern
    is set to 'all', then all experiments will be select.
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
        rsc_filter_name = config.get('ranking_filter',
                                     'rsc_filter_name')
        new_ranking_list = []
        for ranking in ranking_list:
            filtered_ranking = []
            for idx, val in ranking:
                if rsc_filter_name not in kpi_list[idx].resource:
                    filtered_ranking.append((idx, val))
            new_ranking_list.append(filtered_ranking)
        return new_ranking_list
