# -*- coding: utf-8 -*-
"""The module that contains the supercalss of experiment tag.
"""
from abc import abstractmethod


class GeneralExpTag(object):
    """Abstract superclass of experiment tag generator for the arff file.

    Any adoption of experiment filter should inherit this class, and implement
    tag() class method.
    """
    @classmethod
    @abstractmethod
    def tag(cls, exp):
        """Abstract tag class method.

        Classes inherit this class should implement this method, which is
        supposed to contain the user's stratagy of generating the tag for the
        experiment in the arff file.

        Args:
            exp(obj): An util.runtime.Observation instance.

        Returns:
            A string representing the experiment class.
        """
        pass
