# -*- coding: utf-8 -*-
"""The module that contains the ranking oracle that produces the culprit by
summing up the rankings of each resrouce.
"""
from plugins.oracle.general_oracle import GeneralOracle
from util.kpi_info import kpi_list


class SumOracle(GeneralOracle):
    """This Oracle verifies the ranking by the sum of rankings grouped by
    resources.
    """

    @classmethod
    def check(cls, ranking_tuples_list, faulty_rsc, lclz_cnt):

        # print("\nsum oracle. ranking_tuples_list", ranking_tuples_list)

        """Implementation of Check. See class doc for more information.

        Args:
            ranking_tuples_list(list): A list which contains a ranking of KPIs
                oraganized in time sereis, i.e.: [[(${KPI index 1}, ${Ranking
                1}), (${KPI index 2}, ${Ranking 2}), ...], ...].

            faulty_rsc(str): The actual faulty resource. The oracle may use it
                to check if its suspected resource is the actual faulty
                resource.
            lclz_cnt(list): A list of integer, which contains the timestamp(s)
                to verify the rankings.

        Returns:
            A tuple which contains in order the following:
            - A dictionary, whose keys are some boolean property names of the
                verification, e.g. 'successfully spotted', and the values are
                all boolean. At the end of the verification, the percentage of
                the True value over all experiments will be summarized in the
                dst_folder.
            - A list that in order contains the tuples of resource and their
                scores.
            - A string representing the suspect.
        """
        cls.single_result = {}
        ranking_tuples = ranking_tuples_list[lclz_cnt]
        # print("\nsum oracle. ranking_tuples: ", ranking_tuples)
        stat = {}

        for idx, val in ranking_tuples:
            rsc = kpi_list[idx].resource
            cls.__add_ranking(rsc, val)

        # print("\nsum oracle. cls.single_result:", cls.single_result)

        rsc_sorted = sorted(cls.single_result, key=lambda x: cls.single_result[x], reverse=True)
        # print("\nsum oracle. rsc_sorted:", rsc_sorted)

        stat['First Hit'] = rsc_sorted and rsc_sorted[0] == faulty_rsc
        stat['Second Hit'] = len(rsc_sorted) > 1 and rsc_sorted[1] == faulty_rsc
        stat['Third Hit'] = len(rsc_sorted) > 2 and rsc_sorted[2] == faulty_rsc
        # print("\nsum oracle. stat:", stat)

        return stat, rsc_sorted

    @classmethod
    def __add_ranking(cls, rsc, ranking):
        """Sum ranking to self.single_result

        Args:
            rsc(str): the resource to add
            ranking(float): the ranking to add

        Returns:
            None
        """
        if rsc not in cls.single_result:
            cls.single_result[rsc] = 0.0
        cls.single_result[rsc] += ranking
