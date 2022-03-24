# -*- coding: utf-8 -*-
"""The module that contains the ranking oracle that produces the culprit by
considering occurrence in the rankings and the host-guest mapping in the graph.
"""
from plugins.oracle.basic_average_oracle import BasicAverageOracle
import util.localizer_config as localizer_config
from util.localizer_config import config
import util.kpi_info as kpi_info


class ScaleAverageOracle(BasicAverageOracle):
    """This oracle will multiply a parameter to the hosts, with the value defined
    in '[verifier]/<scale_average_parameter>' in the config file.
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
        if localizer_config.component_enabled('host_guest_info'):
            hg_path = localizer_config.get_meta_path('host_guest')
            with open(hg_path) as f:
                pairs = [l.strip().split(':') for l in f]
                hosts, guests = list(zip(*pairs))
        else:
            hosts = []

        counter = {}
        for r in lst:
            if r not in counter:
                counter[r] = 0
            counter[r] += 1

        coef = config.getfloat('oracle', 'scale_average_parameter')
        for r in counter:
            graph_cnt = kpi_info.get_rsc_cnt(r)
            if graph_cnt == 0:
                counter[r] = 0
            else:
                if r in hosts:
                    counter[r] = float(counter[r])/graph_cnt*coef
                else:
                    counter[r] = float(counter[r])/graph_cnt

        cls.local_rsc_cnts = counter

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
