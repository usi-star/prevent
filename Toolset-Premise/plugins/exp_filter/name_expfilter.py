# -*- coding: utf-8 -*-
"""The module that contains the experiment filter class which filters the
experiments by the name of the experiment.
"""
from plugins.exp_filter.general_expfilter import GeneralExpFilter
from util.localizer_config import config


class NameExpFilter(GeneralExpFilter):
    """This class filters experiment by some string pattern in the name.

    Only when the name of the experiemnt contains the pattern, it will be
    processed. This pattern is defined by '[exp_filter]/<name_filter>' in the
    config file. If the pattern is set to 'all', then all experiments will be
    select.
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
        name_filter = [s.strip() for s in
                       config.get('exp_filter', 'name_filter').split(',')]

        if 'all' in name_filter:
            return True
        for name in name_filter:
            if name.lower() not in exp.exp_info['full_name'].lower():
                return False
        return True
