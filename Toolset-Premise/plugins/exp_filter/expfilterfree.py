# -*- coding: utf-8 -*-
"""The module that contains the experiment filter class which does not filter
the experiments.
"""
from plugins.exp_filter.general_expfilter import GeneralExpFilter


class FilterFree(GeneralExpFilter):
    """This class simply keep all experiments without filtering.
    """

    @classmethod
    def filter_(cls, exp):
        """Implementation of filter_. See class doc for more information.

        Args:
            exp(obj): An util.runtime.Observation instance.

        Returns:
            True
        """
        return True
