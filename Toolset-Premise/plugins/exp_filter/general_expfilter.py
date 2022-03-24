# -*- coding: utf-8 -*-
"""The module that contains the supercalss of experiment filter.
"""
from abc import abstractmethod


class GeneralExpFilter(object):
    """Abstract superclass of experiment filter.

    Any adoption of experiment filter should inherit this class, and implement
    filter_() class method.
    """
    @classmethod
    @abstractmethod
    def filter_(cls, exp):
        """Abstract filter_ class method.

        Classes inherit this class should implement this method, which is
        supposed to contain the user's stratagy of filtering out the
        experiments.

        Args:
            exp(obj): An util.runtime.Observation instance.

        Returns:
            True if the experiment can be kept, False if the experiment should
            be ruled out.
        """
        pass
