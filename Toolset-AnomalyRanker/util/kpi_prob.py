# -*- coding: utf-8 -*-
"""The KPI occurrence probability calculator.
"""
import decimal
import util.kpi_info as kpi_info
import util.localizer_log as localizer_log
import util.localizer_config as localizer_config
from util.localizer_config import config


__probs = None
__rsc_cnt = None
__total_len = 0


def init():
    """Preload all possiblilities of the frequency for each resource.

    Args:
        None

    Returns:
        None
    """
    global __probs
    global __rsc_cnt
    global __total_len
    if __probs is not None:
        localizer_log.msg("Probability has been initialized!")
        return

    __probs = {}
    kpi_list = kpi_info.kpi_list

    __total_len = len(kpi_list)
    __rsc_cnt = {}
    # added also (host, guest) pairs
    if localizer_config.component_enabled('host_guest_info'):
        hg_path = localizer_config.get_meta_path('host_guest')
        with open(hg_path) as f:
            pairs = [tuple(l.strip().split(':')) for l in f]
        pair_ref = {}
        for pair in pairs:
            pair_ref[pair[0]] = pair
            pair_ref[pair[1]] = pair
            __rsc_cnt[pair] = 0

    for kpi in kpi_list:
        rsc = kpi.resource
        if rsc not in __rsc_cnt:
            __rsc_cnt[rsc] = 0
        __rsc_cnt[rsc] += 1
        if rsc in pair_ref:
            __rsc_cnt[pair_ref[rsc]] += 1

    rank_selection = config.getint('oracle', 'rank_selection')
    for rsc in list(__rsc_cnt.keys()):
        __probs[rsc] = []
        rsc_total = __rsc_cnt[rsc]
        for i in range(rank_selection + 1):
            all_comb = permutation(__total_len, rank_selection)
            slots_distrb = combination(rank_selection, i)
            comb_rsc = permutation(rsc_total, i)
            comb_other = permutation(__total_len - rsc_total,
                                     rank_selection - i)
            prob = float(slots_distrb) * comb_rsc * comb_other /\
                all_comb
            __probs[rsc].append(prob)


def get_prob(rsc, cnt, rank_len):
    """Get the probability that by random selection, the probability that the a
    given resource appeared in the rankings for exactly a given frequency.

    Args:
        rsc(str): The target resource.
        cnt(int): The frequency, i.e. times it apprears.
        rank_len(int): The length of the rankings.

    Returns:
        The float that represents the probability
    """
    global __probs
    global __rsc_cnt
    global __total_len

    if not __probs:
        init()

    rank_selection = config.getint('oracle', 'rank_selection')
    rank_top = config.getboolean('oracle', 'rank_top')
    if rank_top and rank_len == rank_selection:
        if rsc not in __probs or cnt >= len(__probs[rsc]):
            localizer_log.error("Prob query out of Index!")

        return __probs[rsc][cnt]
    else:
        all_comb = decimal.Decimal(permutation(__total_len, rank_len))
        slots_distrb = decimal.Decimal(combination(rank_len, cnt))
        rsc_total = __rsc_cnt[rsc]
        comb_rsc = decimal.Decimal(permutation(rsc_total, cnt))
        comb_other = decimal.Decimal(permutation(__total_len - rsc_total,
                                                 rank_len - cnt))
        prob = slots_distrb * comb_rsc * comb_other /\
            all_comb
        return float(prob)


def permutation(n, r):
    """Returns the permutation.
    
    Args:
        n(int): The total number.
        r(int): The number to permutate.
    """
    if n >= r:
        mul = 1
        for i in range(r):
            mul *= n
            n -= 1
        return mul
    else:
        return permutation(n, n)


def combination(n, r):
    """Returns the combination.

    Args:
        n(int): The total number.
        r(int): The number to combine.
    """
    if r == 0:
        return 1
    elif n >= r:
        return permutation(n, r)/permutation(r, r)
    else:
        return combination(n, n)
