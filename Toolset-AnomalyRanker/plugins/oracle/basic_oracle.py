# -*- coding: utf-8 -*-
"""The module that contains the ranking oracle that produces the culprit by
simply counting the occurrence.
"""
from collections import Counter
from plugins.oracle.general_oracle import GeneralOracle
import util.localizer_config as localizer_config
from util.localizer_config import config


class BasicOracle(GeneralOracle, object):
    """This class produces the cluprit by the occurence of resources in the
    rankings.

    If '[oracle]/<rank_top>' in the config file is set to true, then it will
    pick the top ranked N KPIs(N is defined in '[oracle]/<rank_selection>'),
    otherwise it will pick all rankings. Then it will count the occourrence of
    the resources, and produce the one with most apprearance as the culprit.

    If '[oracle]/<host_guest>' is set, it will also read the file in the meta
    folder that includes the host guest map, and produce an extra ranking,
    'i.e. meadium ranking list'.
    """
    __rsc_map = {}
    if localizer_config.component_enabled('host_guest_info'):
        hg_file = localizer_config.get_meta_path('host_guest')
        with open(hg_file) as f:
            lines = [l.strip() for l in f]
            for line in lines:
                terms = line.split(':')
                if len(terms) == 2:
                    host = terms[0].strip()
                    guest = terms[1].strip()
                    __rsc_map[host] = (host, guest)
                    __rsc_map[guest] = (host, guest)

    @classmethod
    def check(cls, ranking_tuples_list, faulty_rsc, lclz_cnt):
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
        # Initialize result
        result = {
            'strong_success': False,
            'strong_fail': False,
            'strong_miss': False,
            'medium_success': False,
            'medium_fail': False,
            'medium_miss': False,
        }

        ranking_tuples = ranking_tuples_list[lclz_cnt]
        # print("\nOracle. KPIs sorted by rank:", ranking_tuples)

        # Deal with empty set
        if not ranking_tuples:
            if faulty_rsc == 'N/A':
                result['strong_success'] = True
                result['medium_success'] = True
            else:
                result['strong_fail'] = True
                result['medium_fail'] = True
            return result, ranking_tuples, None

        rank_top = config.getboolean('oracle', 'rank_top')
        if rank_top:
            rank_selection = config.getint('oracle', 'rank_selection')  # 20 (or more) top ranked KPIs
            ranking_rsc = cls.strip(ranking_tuples)[:rank_selection]
        else:
            ranking_rsc = cls.strip(ranking_tuples)

        # print("\nOracle. Resources of the top ranked KPIs:", ranking_rsc)

        strong_check, strong_suspect, strong_suspect_list = cls.sub_check(ranking_rsc, faulty_rsc)

        if strong_check:
            result['strong_success'] = True
        elif strong_check is False:
            result['strong_fail'] = True
        elif strong_check is None:
            result['strong_miss'] = True

        medium_ranking = [cls.__rsc_map[r] if r in cls.__rsc_map else r for r in ranking_rsc]

        if faulty_rsc in cls.__rsc_map:
            medium_check, medium_suspect, medium_suspect_list = \
                cls.sub_check(medium_ranking, cls.__rsc_map[faulty_rsc])
        else:
            medium_check, medium_suspect, medium_suspect_list = \
                cls.sub_check(medium_ranking, (faulty_rsc))

        if medium_check:
            result['medium_success'] = True
        elif medium_check is False:
            result['medium_fail'] = True
        elif medium_check is None:
            result['medium_miss'] = True

        return result, strong_suspect_list, strong_suspect

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
        counter = Counter(lst).most_common()  # keys - resources, values - number of entry of the resource to the list. All resources are considered.
        couter_dicts = dict(counter)
        # print("\nOracle. Resources sorted by the number of KPIs in top ranked KPIs list: ", couter_dicts)

        suspect_list = list(zip(list(couter_dicts.keys()), list(couter_dicts.values())))
        # print("\nOracle. Suspect_list: ", suspect_list)

        # A dict that maps count to resources
        rev_cnt = {}
        for (term, cnt) in counter:
            if cnt not in rev_cnt:
                rev_cnt[cnt] = []
            rev_cnt[cnt].append(term)

        max_app = max(rev_cnt.keys())

        if len(rev_cnt[max_app]) == 1:  # if there is a absolute leader amount the resources
            if rev_cnt[max_app][0] == rsc:
                return True, rsc, suspect_list
            else:
                return False, rev_cnt[max_app][0], suspect_list
        else:
            if rsc == 'None':
                return True, 'None', suspect_list

            return None, None, suspect_list
