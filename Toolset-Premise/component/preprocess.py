# -*- coding: utf-8 -*-
"""The module that manages the preprocessing.
"""
import os
import time
import util.localizer_log as localizer_log
from util.localizer_config import config
import util.localizer_config as localizer_config
import util.kpi_info as kpi_info


def preprocess():
    """The main API of the preprocess component.

    It will take the log files of SCAPI which contains the anomalies, and
    transform it to the foramat that users and the predictor/localizer can
    read. After transformation, it will split the anomalies at different
    timestamps to differnet txt files, with each filename corresponds to the
    timestamp.

    Args:
        None

    Returns:
        None
    """
    main_folder = localizer_config.get_folder('src')
    localizer_config.reset_path(main_folder)
    targets = config.get('preprocess', 'targets').split(',')
    for target in targets:
        localizer_log.msg("Preprocessing {tar}...".format(tar=target))
        process_folder(target)


def extractAnomaly(exp_name, src_dir):
    """Extract the anomaly from the SCAPI log file.

    Some information defined in the config file wil be used to assist.
    '[preprocess]/<log_file_name>' defines the name of the SCAPI log file.
    '[preprocess]/<anomaly_string>' defines the pattern to recognize a line
    that contains the anomaly information, '[preprocess]/<fault_start>' defines
    the start time of the experiment so the method knows when to start the
    extraction.

    Args:
        exp_name(str): the name of the experiment.
        src_dir(str): The name of the folder where the experiment is put.

    Returns:
        A list of sets, each set represent the anomalies (i.e. indices of KPIs)
        at the timestamp.
    """
    log_file_name = config.get('preprocess', 'log_file_name')
    anomaly_string = config.get('preprocess', 'anomaly_string')
    fault_start = config.get('preprocess', 'fault_start')
    anmlist = {}

    log_file = os.path.join(src_dir, exp_name, log_file_name)

    anomalies_file = open(log_file)
    lines = [x for x in anomalies_file if anomaly_string in x]

    ts_start = int(time.strftime('%s', time.strptime(fault_start, "%y%m%d")))

    for line in lines:
        line = line.split(',')

        gcd = int(line[4])
        kpi = kpi_info.get_kpi_by_id(gcd)

        # substract 3600 due to GMT time
        # TODO: make this more general
        reflex_time = int(line[2])/1000 - ts_start - 3600
        if reflex_time not in anmlist:
            anmlist[reflex_time] = []
        anmlist[reflex_time].append(kpi.tag)

    for ts, anmls in anmlist.items():
        anmlist[ts] = set(sorted(anmls))

    return anmlist


def process_exp(exp_name, src_dir, dst_dir):
    """Process a single experiment's data.

    Args:
        exp_name(str): The name of the folder of a single experiment.
        src_dir(str): The name of the folder where the experiment is put.
        dst_dir(str): The name of the folder where the files after processing
            are put.

    Returns:
        None
    """
    anomalies = extractAnomaly(exp_name, src_dir)
    end_time = int(max(anomalies.keys()))

    dst_exp_dir = os.path.join(dst_dir, exp_name)
    localizer_config.reset_path(dst_exp_dir)

    # 7200 for default (2h) or more for longer experiments
    for t in range(0, max(7200, end_time + 300), 300):
        dst = os.path.join(dst_exp_dir, str(t) + '.txt')
        f = open(dst, 'w')

        lines = []
        if t in anomalies:
            for anomaly in anomalies[t]:
                lines.append(str(anomaly) + '\n')
        f.writelines(lines)

        f.close()


def process_folder(target):
    """Process a folder's data.

    Args:
        target(str): The folder name. This folder should be put under the
            preprocess folder, and it should contains the experiemtns' log
            files, each experiment a subfolder.

    Returns:
        None
    """
    preprocess_dir = localizer_config.get_scapidata_path(target)
    dst_dir = os.path.join(localizer_config.get_folder('src'),
                           target)

    localizer_config.reset_path(dst_dir)

    experiments = [x for x in os.listdir(preprocess_dir)
                   if os.path.isdir(os.path.join(preprocess_dir, x))]

    for exp in experiments:
        process_exp(exp, preprocess_dir, dst_dir)


if __name__ == '__main__':
    preprocess()
