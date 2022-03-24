# -*- coding: utf-8 -*-
"""The module that contains the experiment filter class which filters the
experiments by the faulty resource of the experiment.
"""
from plugins.exp_filter.general_expfilter import GeneralExpFilter
from util.localizer_config import config


class RscExpFilter(GeneralExpFilter):
    """This class filters experiment by resource pattern in the name.

    Only when the name of the experiemnt contains the resource pattern in its
    resource part, it will be processed. This resource pattern is defined by
    '[exp_filter]/<rsc_filter>' in the config file. If the pattern is set to
    'all', then all experiments will be select.
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
        rsc_filter = config.get('exp_filter', 'rsc_filter')
        if rsc_filter.lower() == 'all':
            return True
        if rsc_filter.lower() == exp.exp_info['faulty_resource'].lower():
            return True
        return False
