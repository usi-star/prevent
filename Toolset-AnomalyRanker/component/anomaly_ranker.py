# -*- coding: utf-8 -*-
"""The module that manages ranking the anomalies.
"""
import os
import util.localizer_log as localizer_log
import util.localizer_config as localizer_config
from util.localizer_config import config
import util.kpi_info as kpi_info


def rank_exp(exp, dst_folder):
    """Rank an experiment in a folder with rankers provided.

    Args:
        exp(obj): an util.runtime.Observation object.
        dst_folder(str): the folder to log the ranking result.

    Returns:
        The rankings as a dictionary, where the keys are the name of the
        rankers and the values are the ranking in the form of a list in time
        series, such as [[${KPI index 1}, ${KPI ranking 1}, ${KPI index 2},
        ${KPI ranking 2}, ...], ...]
    """
    ranking_cache = localizer_config.load_cache('rankings',
                                                exp.exp_info['full_name'])
    if ranking_cache:
        rankings = ranking_cache
    else:
        rankers = [ranker.strip() for ranker in
                   config.get('ranker', 'rankers').split(',')]

        rankings = {}
        for ranker_name in rankers:
            # TODO: check if is fine to make rankers global so
            # there is no need to import it every exp
            ranker = localizer_config.get_plugin('ranker', ranker_name)
            result = single_rank(exp,
                                 ranker)
            rankings[ranker_name] = result

        localizer_config.save_cache(rankings,
                                    'rankings',
                                    exp.exp_info['full_name'])

    log_rankings(exp, rankings, dst_folder)
    return rankings


def single_rank(exp, ranker):
    """Use the given ranker to rank a single experiment's data.

    Args:
        exp(obj): an util.runtime.Observation object.
        ranker(obj): a subclass of plugins.ranker.general_ranker

    Returns:
        the ranking in the form of a list in time
        series, such as [[${KPI index 1}, ${KPI ranking 1}, ${KPI index 2},
        ${KPI ranking 2}, ...], ...]
    """
    results = []

    for exp_data in exp.exp_data:
        kpis, values = ranker().rank(exp_data)
        results.append(list(zip(kpis, values)))

    return results


def log_rankings(exp, rankings, dst_folder):
    """Log the ranking results to some files each file corresponding to a
    ranking algorithm

    Args:
        exp(obj): an util.runtime.Observation object.
        rankings(list): the ranking in the form of a list in time
            series, such as [[${KPI index 1}, ${KPI ranking 1}, ${KPI index 2},
            ${KPI ranking 2}, ...], ...]
        dst_folder(str): the folder to log the ranking result.

    Returns:
        None
    """
    exp_len = len(exp.time_list)
    preditions = exp.prediction_seq
    for ranker_name in rankings:
        ranking_lst = rankings[ranker_name]
        if not len(ranking_lst) == exp_len:
            localizer_log.error(("Ranking lenth not equal to "
                                 "experiment data length"))

        f_path = os.path.join(dst_folder, ranker_name + '.txt')
        with open(f_path, 'w') as f:
            for cnt in range(exp_len):
                time = exp.time_list[cnt]
                no_anomalies = len(exp.exp_data[cnt])
                prediction = \
                    preditions[cnt] if cnt < len(preditions) else 'N/A'

                line = '[Time: {t}][Anomalies {no}][Prediction: {pred}]\n'\
                    .format(t=str(time).rjust(5),
                            no=str(no_anomalies).rjust(3),
                            pred=str(prediction))
                f.write(line)
                f.write('\t[Rankings:]\n')

                for idx, val in ranking_lst[cnt]:
                    kpi = kpi_info.get_kpi_by_id(idx)

                    line = '\t{kpi_name}:{value}\n'\
                        .format(kpi_name=str(kpi), value=val)
                    f.write(line)
