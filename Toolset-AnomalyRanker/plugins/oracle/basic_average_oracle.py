# -*- coding: utf-8 -*-
"""The module that contains the ranking oracle that produces the culprit by
considering occurrence in the rankings and their frequency in the graph.
"""
from plugins.oracle.basic_oracle import BasicOracle
import util.kpi_info as kpi_info


class BasicAverageOracle(BasicOracle):
    """Same as BasicOracle, but divide the number of resources shown in the list
    by the total count of the resource in the global kpi lists.
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
        counter = {}
        for r in lst:
            if r not in counter:
                counter[r] = 0
            counter[r] += 1

        for r in counter:
            graph_cnt = kpi_info.get_rsc_cnt(r)
            if graph_cnt == 0:
                counter[r] = 0
            else:
                counter[r] = float(counter[r])/graph_cnt

        rev_cnt = {}
        for term, cnt in counter.items():
            if cnt not in rev_cnt:
                rev_cnt[cnt] = []
            rev_cnt[cnt].append(term)

        max_app = max(rev_cnt.keys())
        if len(rev_cnt[max_app]) == 1:
            if rev_cnt[max_app][0] == rsc:
                return True, rsc
            else:
                return False, rev_cnt[max_app]
        else:
            if rsc == 'None':
                return True, 'None'
            else:
                return None, None
