# -*- coding: utf-8 -*-
"""The module that manages filtering the experiments.
"""
import util.localizer_config as localizer_config
from util.localizer_config import config


def filter_(exp_map):
    """Take the experiments and apply some filters (defined in the config file,
    see description of the config file in README for more information)

    Args:
        exp_map(dict): The dictionary where the keys are integers represent the
        id of the experiment and the values are util.runtime.Observation
        object.

    Returns:
        A new dictionary with the filtered experiments removed.
    """
    filter_name = config.get('exp_filter', 'filter')
    filter_klass = localizer_config.get_plugin('exp_filter',
                                               filter_name)
    new_map = {}
    for exp_id, exp in exp_map.items():
        if filter_klass.filter_(exp):
            new_map[exp_id] = exp

    return new_map
