# -*- coding: utf-8 -*-
"""The module that contains the ranking oracle that produces the culprit by
considering occurrence in the rankings and their probability of occurrence by
rankdom in the graph.
"""
from collections import Counter
from plugins.oracle.basic_oracle import BasicOracle
import util.kpi_prob as kpi_prob


class BasicProbOracle(BasicOracle):
    """Same as BasicOracle, but rank by the probility of occurence of resources,
    the lower, the more likely problematic.
    """
    @classmethod
    def sub_check(cls, lst, rsc):
        """A helper class method to check if the suspect in the resource list
        is the given one. For more information, refer to the doc of the class.

        Args:
            lst(list): A list of resources.
            rsc(str): The string representing the faulty resource.

        Return:
            A boolean which is:
            - True if the ONLY most suspected resource in lst is rsc
            - False if the ONLY most supected resource in lst is not rsc
            - None if there is more than one most suspected resources in lst,
                or lst is empty.
        """
        counter = dict(Counter(lst))

        probs = {}
        for r, occr in counter.items():
            probs[r] = kpi_prob.get_prob(r, occr, len(lst))

        sort_rsc = sorted(list(probs.keys()),
                          key=lambda k: probs[k])
        suspect_list = [(r, 1 - probs[r]) for r in sort_rsc]

        assert not sort_rsc
        # miss
        if len(sort_rsc) > 1 and \
                probs[sort_rsc[0]] == probs[sort_rsc[1]]:
            # if failurefree, miss is a hit
            if rsc == 'None':
                return True, 'None'
            return None, None, suspect_list
        # success
        if sort_rsc[0] == rsc:
            return True, rsc, suspect_list

        # fail
        return False, sort_rsc[0], suspect_list
