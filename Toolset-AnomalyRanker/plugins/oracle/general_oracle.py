# -*- coding: utf-8 -*-
"""The module that contains the supercalss of ranking oracle.
"""
from abc import abstractmethod
import util.kpi_info as kpi_info


class GeneralOracle(object):
    """Abstract superclass of ranking oracle.

    Any adoption of raning oracle should inherit this class, and implement
    check() class method.
    """
    @classmethod
    @abstractmethod
    def check(cls, ranking_tuples_list, faulty_rsc, lclz_cnt):
        """Abstract check class method.

        Classes inherit this class should implement this method, which is
        supposed to contain the user's stratagy of finding the culprit from the
        rankings and possibly verifying the answers.

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
        pass

    @classmethod
    def strip(cls, ranking_tuples):
        """
        A helper class method for oracle classes, that transforms a list of
        KPIs to a list of resources.

        Args:
            ranking_tuples(list): A list of KPIs, with every element a (${KPI
                id}, ${ranking}) tuple.

        Retrurns:
            A list of resourse correspondingt to the KPIs of the input.
        tuples.
        """
        result_lst = []
        for (idx, ranking) in ranking_tuples:
            # get the resource from (resource, metric) tuple
            result_lst.append(kpi_info.kpi_list[idx].resource)

        return result_lst
