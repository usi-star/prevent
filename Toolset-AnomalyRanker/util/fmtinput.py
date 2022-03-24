# -*- coding: utf-8 -*-
"""The modlue that formats the input of anomaly files to binary array for the
predictor.

Attributes:
    PreData(obj): The structure to store the data after foramtting. It is a
        Python Namedtuple, with three elements: 'exp_obj' is the
        util.runtime.Observation object of the experiemnt, 'time' is a list of
        list of 0/1 in which 1 indicates that the KPI at that index is
        anomalous.
"""
import os
from collections import namedtuple
import util.kpi_info as kpi_info
import util.localizer_log as localizer_log
import util.localizer_config as localizer_config

PredData = namedtuple('PredData', ['exp_obj', 'time', 'data'])


def fmt_folder(folder):
    """Format the experiment in a folder.

    Args:
        folder(str): The name of the folder to be format, which should contains
            the folders, each folder represents an experiemnt.

    Returns:
        A list of PredData containing the data.
    """
    result = []

    folder_dir = localizer_config.get_src_path(folder)
    if not os.path.isdir(folder_dir):
        localizer_log.error("folder " + folder + ' not exist. Abort.')

    experiments = [x for x in os.listdir(folder_dir)
                   if os.path.isdir(os.path.join(folder_dir, x))]

    list_size = len(kpi_info.kpi_list)
    import util.runtime as runtime
    for exp_name in experiments:
        exp = runtime.find_exp_by_name(exp_name)
        if not exp:
            localizer_log.warning("Experiment {exp} not found"
                                  .format(exp=exp_name))
            continue
        exp_dir = os.path.join(folder_dir, exp_name)
        files = [x for x in os.listdir(exp_dir) if x.endswith('.txt')]
        timeset = [int(filename.strip().replace('.txt', ''))
                   for filename in files]

        for t in sorted(timeset):
            lst = [0 for i in range(list_size)]
            with open(os.path.join(exp_dir, str(t) + '.txt')) as f:
                for l in f:
                    idx = kpi_info.get_index(l.strip())
                    lst[idx] = 1
            result.append(PredData(exp, str(t), lst))

    return result


if __name__ == '__main__':
    fmt_folder('faulty', 300)
