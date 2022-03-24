# -*- coding: utf-8 -*-
"""The module that contains the experiment tag class which give a tag/class for
the experiment in the use of arff file."""
from plugins.exp_tag.general_exptag import GeneralExpTag


class TypeLocationExpTag(GeneralExpTag):
    """This class generates a tag for an experiment with its fault type and
    faulty location.
    """
    @classmethod
    def tag(cls, exp):
        """Implementation of tag. See class doc for more information.

        Args:
            exp(obj): An util.runtime.Observation instance.

        Returns:
            A string representing the experiment class.
        """
        return '{ftype}_{flocation}'\
            .format(ftype=exp.exp_info['fault_type'],
                    flocation=exp.exp_info['faulty_resource'])
