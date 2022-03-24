# -*- coding: utf-8 -*-
"""The module that contains the experiment filter class which filters the
experiments by the number of anomalies.
"""
from plugins.exp_filter.general_expfilter import GeneralExpFilter
from util.localizer_config import config


class AnomalySizeExpFilter(GeneralExpFilter):
    """This class filters experiment by the size of anomaly sets.

    If the maximum number of anoamlies at some timestamp excceeds a threslhod.
    This threslhod is defined by '[exp_filter]/<anomaly_threshold>' in the
    config file.
    """
    @classmethod
    def filter_(cls, exp):
        """Implementation of filter_. See class doc for more information.

        Args:
            exp(obj): An util.runtime.Observation instance.

        Returns:
            True if the experiment can be kept, False if the experiment should
            be ruled out.
        """
        anomaly_threshold = config.getint('exp_filter', 'anomaly_threshold')
        return any([len(s) > anomaly_threshold for s in exp.exp_data])
