# -*- coding: utf-8 -*-
"""The module that reads the runtime anomalies of multiple experiments

Attibutes:
    targets_experiments(dict): A dictionary which maps the id of an target
        experiment to its Observation class.

    all_experiments(dict): A dictionary which maps the id of an experiment (can
        be from the training set, validation set or target set) to its
        Observation class.
"""
import os
import util.localizer_log as localizer_log
import util.kpi_info as kpi_info
import util.localizer_config as localizer_config
from util.localizer_config import config
from component.predict import check_stable_prediction

targets_exps = {}
all_exps = {}


def add_folder(folder, group):
    """Read all experiments in a folder.

    The folder must contain experiment subfolders which are named in the format
    of: ${experiment id}-${IP of the injected node}-${fault type}_${hostname of
    the injected fault}_${other parameters}

    Args:
        folder(str): The folder to read from.
        group(dict): The target global variable to put the result.

    Returns:
        None
    """
    if not os.path.exists(folder):
        localizer_log.error("Experiments Folder {folder_name} not exist!"
                            .format(folder_name=folder))

    for f in [x for x in os.listdir(folder)
              if os.path.isdir(os.path.join(folder, x))]:
        add_exp(os.path.join(folder, f), group)


def add_target(folder):
    """Read the experiments from a folder and put the results to targets_exps.

    Args:
        folder(str): The folder to read from.

    Returns:
        None
    """
    global targets_exps
    add_folder(folder, targets_exps)


def add_all(*args):
    """Read the experiments from a folder and put the results to all_exps.

    Args:
        args(tuple): The tuple containing the folders(strings) to read from.

    Returns:
        None
    """
    global all_exps
    cache = localizer_config.load_cache('runtime', 'all_exps')
    if cache:
        all_exps = cache
    else:
        for folder in args:
            add_folder(folder, all_exps)
        localizer_config.save_cache(all_exps, 'runtime', 'all_exps')


def add_exp(exp_dir, group):
    """Read the data of a single experiment folder.

    Args:
        exp_dir(str): The experiment folder to read from.
        group(dict): The target global variable to put the result.

    Returns:
        None
    """
    global all_exps

    if not validate_exp_dir(exp_dir):
        localizer_log.warning('Directory ' + exp_dir + ' not valid. Skip.')
        return

    exp_name = os.path.split(exp_dir)[-1]
    exp_id = int(exp_name.split('-')[0])

    if group is all_exps:
        exp = Observation(exp_dir, exp_name, exp_id)
        all_exps[exp_id] = exp
    elif exp_id in all_exps:
        group[exp_id] = all_exps[exp_id]
    else:
        exp = Observation(exp_dir, exp_name, exp_id)
        group[exp_id] = exp


def validate_exp_dir(exp_dir):
    """Check if the name of the experiment's directory is in correct form.

    Args:
        exp_dir(str): The experiment folder to check.

    Returns:
        True if the name is in correct format, otherwise False.
    """
    folder = os.path.split(exp_dir)[-1]
    sections = folder.split('-')
    if len(sections) >= 3 and \
            sections[0].isdigit() and \
            len(sections[0]) == 10 and \
            len(sections[1].split('.')) == 4 and \
            len(sections[2].split('_')) >= 3:
        return True
    return False


def add_predictions(predictions):
    """Attch the prediction results to the experiemtns' objects.

    Args:
        predictions(dict): A dictionary where the keys are the indices of the
            experiments(see util.runtime.Observation for more details), and the
            values are list of the predictoins corresponding to the anomaly
            list. This list only contains True and/or False, True indicates a
            prediction.

    Returns:
        None
    """
    global all_exps
    for idx in predictions:
        if idx in all_exps:
            all_exps[idx].add_prediction(predictions[idx])


def find_exp_by_name(exp_name):
    """Find the experiment objects by name.

    Args:
        exp_name(str): The name of the experiment.

    Returns:
        The experiment object, i.e. an Observation object.
    """
    global all_exps
    idx = next((x for x in list(all_exps.keys()) if str(x) in exp_name),
               None)
    return all_exps[idx] if idx else None


class Observation(object):
    """This class stores runtime information of a single experiment.

    Runtime information of an experiment mainly contains experiment basic
    information such as faulty type and faulty resource, as well as the
    anomalies sets which are organized in time series. It also provide optional
    extra information, such as predictions, rankings.

    Args:
        exp_dir(string): The directory which contains the anomaly files of the
            experiment. The anomaly files must be named in the form of
            {time}.txt, and have each line representing a KPI in the form of
            ('${resource_name}', '${group_name}', '${metric name}')
        exp_name(string): Experiment name, whcich must follows the pattern
            ${timestamp}-${IP}-${fault type}-${faulty resource}-${fault
            parameter}
        exp_id(string): Id of the experiment, typically the ${timestamp} part
        of the exp_name.

    Attributes:
        exp_info(dict): The dictionary contains several experiment
            informations: 'id' indicates the index, 'full_name' indicates the
            full name, 'faulty_type' indicates the type of fault, 'faulty
            resource' indicates the resource that the fault is injected on,
            'prediction_border' is the time(index in time_list) that the
            predictor gives a prediction, 'prediction' indicates whether the
            experiment is predicted as faulty.
        time_list(list): The timestamps that maps to the data in exp_data.
        exp_data(list): The anomaly sets organized in time series as a list.
            Each element in the list is the anomalies at a timestamp, which is
            a set that contains the indices of the KPIs.
        exp_data_inc(list): The same as exp_data, but only contains the
            anomalies that are not present in the prevous timestamp.
        prediction_seq(list): The list contains the predictions at each
            timestamp corresponding to time_list and exp_data.
        rankings(dict): The dictionary contains the rankings of different
            algorithms, in the form of {'{algorithm 1}': [[], [], [(${KPI 1},
            ${ranking}), ${KPI 2}, ${ranking}...], ...], '{algorithm 2}': ...}
    """
    def __init__(self, exp_dir, exp_name, exp_id):
        self.exp_info = {}
        self.time_list = []
        self.exp_data = []
        self.exp_data_inc = []
        self.prediction_seq = []
        self.rankings = {}

        self.exp_info['id'] = exp_id
        self.exp_info['full_name'] = exp_name

        if not os.path.isdir(exp_dir):
            localizer_log.error('Initializting Oberservation for ' +
                                exp_dir + ': Folder not found')
            return

        self.add_info(exp_name)
        self.add_data(exp_dir)

    def add_info(self, exp_name):
        """Add infomations from the experiment name

        Args:
            exp_name(str): The name of the experiment.

        Returns:
            None
        """
        # Read faulty or not
        if config.get('default', 'nonfaulty_pattern') in exp_name:
            faulty = False
        else:
            faulty = True
        self.exp_info['faulty'] = faulty

        # Fault type
        name_sections = exp_name.split('-')
        fault_infos = name_sections[2].split('_')
        if faulty:
            self.exp_info['fault_type'] = fault_infos[0]
            self.exp_info['faulty_resource'] = fault_infos[1]
        else:
            self.exp_info['fault_type'] = 'Failure Free'
            self.exp_info['faulty_resource'] = 'N/A'

    def add_data(self, exp_dir):
        """Add data from the experiment source data folder.

        Args:
            exp_dir(str): The path of hte source data folder.

        Returns:
            None
        """
        time_series = sorted([int(f.replace('.txt', '')) for f in
                              [x for x in os.listdir(exp_dir) if '.txt' in x]])
        self.time_list = time_series

        # The set that contains all appeared anomalies
        self.appeared_anomalies = set()

        for t in time_series:
            fname = os.path.join(exp_dir, str(t) + '.txt')
            with open(fname) as f:
                anomalies = [kpi_info.get_index(line.strip())
                             for line in f]
            self.exp_data.append(set(anomalies))

            for anml in anomalies:
                self.appeared_anomalies.add(anml)

        for i, data in enumerate(self.exp_data):
            if i == 0:
                self.exp_data_inc.append(set())
            else:
                self.exp_data_inc.append(self.exp_data[i] -
                                         self.exp_data[i-1])

    def add_prediction(self, prediction):
        """Add prediction.

        Args:
            prediction(list): A list of the predictoins corresponding to the
            anomaly list. This list only contains True and/or False, True
            indicates a prediction.

        Returns:
            None
        """
        self.prediction_seq = prediction

        t, pred = check_stable_prediction(prediction)

        self.exp_info['prediction_border'] = t
        self.exp_info['prediction'] = pred

    def add_rankings(self, rankings):
        """Add rankings.

        Args:
            rankings(dic): The rankings as a dictionary, where the keys are the
                name of the rankers and the values are the ranking in the form
                of a list in time series, such as [[${KPI index 1}, ${KPI
                ranking 1}, ${KPI index 2}, ${KPI ranking 2}, ...], ...]

        Returns:
            None
        """
        if isinstance(rankings, dict):
            self.rankings = rankings
        else:
            localizer_log.warning("Rankings should be dictionary type!")
