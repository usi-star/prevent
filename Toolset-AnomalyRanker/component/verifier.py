# -*- coding: utf-8 -*-
"""The module that manages the oracles.

Attibutes:
    global_stat(dict): A dictionary of dictionary. In the outer dictionary, the
        keys are the names of the rankers. In the inner dictionary, the keys
        are the properties returned by the oracle (see
        plugins.orable.basic_oracle), and the values are the number of True
        values in these experiments.
    total_cnt(dict): A dictionary, in which the keys are the names of the
        rankers, the values are the number of expriments the rank ranks.
"""
import os
import util.localizer_log as localizer_log
import util.kpi_info as kpi_info
import util.localizer_config as localizer_config
from util.localizer_config import config


global_stat = {}
total_cnt = {}


def verify(exp, dst_folder):
    """Verify the ranking by checking the culprit resource from the ranking.

    The results will be written to the dst folder (see doc of the config file
    in README)

    Args:
        exp(obj): A util.runtime.Observation object.
        dst_folder(str): The folder to write the results.

    Returns:
        None
    """
    global total_cnt
    global global_stat

    ranking_maps = exp.rankings

    rankingtime_selector = config.get('rankingtime', 'selector')
    selector = localizer_config.get_plugin('rankingtime',
                                           rankingtime_selector)

    oracle_name = config.get('oracle', 'oracle')
    oracle = localizer_config.get_plugin('oracle',
                                         oracle_name)

    for ranker, ranking_tuples_list in ranking_maps.items():
        lclz_cnt = selector.gettime(exp, ranker)
        if lclz_cnt < 0:
            localizer_log.msg('Cannot select a localization time. Skipped.')
            continue

        if ranker not in total_cnt:
            total_cnt[ranker] = 0
        total_cnt[ranker] += 1

        if ranker not in global_stat:
            global_stat[ranker] = {}
        fault_rsc = exp.exp_info['faulty_resource']
        single_check, suspected_list, strong_sus = \
            oracle.check(ranking_tuples_list,
                         fault_rsc,
                         lclz_cnt)
        for check_term, result in single_check.items():
            if check_term not in global_stat[ranker]:
                global_stat[ranker][check_term] = 0
            if result:
                global_stat[ranker][check_term] += 1

        log_verifications(dst_folder,
                          ranker,
                          exp,
                          lclz_cnt,
                          suspected_list,
                          single_check)


def log_verifications(dst_folder,
                      ranker_name,
                      exp,
                      cnt,
                      suspected_list,
                      result):
    """Write the result of a single experiment to file.

    Args:
        dst_folder(str): The folder to write the results.
        ranker_name(str): The name of the ranker. Each result of a ranker will
            be put in a singel file.
        exp(obj): An util.runtime.Observation object.
        cnt(int): The time for localizaiton. Used for logging the prediction at
            the time.
        suspected_list(list): A list that in order contains the tuples of
            resource and their scores.
        result(dict): The result of the verification. Noramly it is the
            dictionary, whose keys are some boolean property names of the
            verification, e.g. 'successfully spotted', and the values are all
            boolean. At the end of the verification, the percentage of the True
            value over all experiments will be summarized in the dst_folder.

    Returns:
        None
    """
    f_path = os.path.join(dst_folder, ranker_name + '.txt')
    with open(f_path, 'w') as f:
        if cnt < len(exp.prediction_seq):
            prediction = str(exp.prediction_seq[cnt])
        else:
            prediction = 'N/A'
        str_anomalies = str([str(kpi_info.kpi_list[idx])
                             for idx in exp.exp_data[cnt]])

        f.write('Predictions: {pred}\n'.format(pred=prediction))
        f.write('Picking Timestamp: {t}\n'.format(t=str(cnt)))
        f.write('Anomalies: {anm}\n'.format(anm=str_anomalies))
        f.write('Faulty node: {f_node}\n'
                .format(f_node=exp.exp_info['faulty_resource']))
        f.write('Ranking Count: {r_cnt}\n'.format(r_cnt=str(suspected_list)))
        f.write('Verify_result: {res}'.format(res=str(result)))


def final_stat(dst_file):
    """
    write result to final results
    """
    global global_stat
    stat_file = os.path.join(dst_file)
    with open(stat_file, 'w') as f:
        for ranker, ranker_stat in global_stat.items():
            f.write('Ranker: {r_name}\n'.format(r_name=ranker))
            for term in ranker_stat:
                stat_term = float(global_stat[ranker][term])/total_cnt[ranker]
                f.write('{term} rate: {stat}\n'
                        .format(term=term, stat=stat_term))
            f.write('\n')
