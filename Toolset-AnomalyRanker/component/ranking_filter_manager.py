# -*- coding: utf-8 -*-
"""The module that manages filtering the rankings.
"""
import util.localizer_config as localizer_config
from util.localizer_config import config


def filter_(exp, rankings):
    """Take an experiment's ranking and apply some filters (defined in the
    config file, see description of the config file in README for more
    information)

    Args:
        exp(obj): an util.runtime.Observation object.
        rankings(dict): The rankings as a dictionary, where the keys are the
        name of the rankers and the values are the ranking in the form of a
        list in time series, such as [[${KPI index 1}, ${KPI ranking 1}, ${KPI
        index 2}, ${KPI ranking 2}, ...], ...]

    Returns:
        A new ranking dictionary with the filtered rankings removed.
    """
    filters_names = [f.strip() for f in
                     config.get('ranking_filter', 'filters').split(',')]
    filters = []
    for filter_name in filters_names:
        filter_klass = localizer_config.get_plugin('ranking_filter',
                                                   filter_name)
        filters.append(filter_klass)

    new_rankings = {}
    for ranker, ranking_list in rankings.items():
        tmp_rankings = ranking_list
        for filter_klass in filters:
            tmp_rankings = filter_klass.filter_(exp, tmp_rankings)
        new_rankings[ranker] = tmp_rankings
    return new_rankings
