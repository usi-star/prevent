# -*- coding: utf-8 -*-
"""The module that manages the predictor.
"""
import util.localizer_log as localizer_log
import util.localizer_config as localizer_config
from util.localizer_config import config
import util.fmtinput as fmtinput


def run():
    """Main API of the predictor. 
    
    Format the training data, verification data and target data, then train and
    run the predictor. At the end print a statistical summary of the prediction
    results.

    Args:
        None

    Returns:
        A dictionary where the keys are the indices of the experiments(see
        util.runtime.Observation for more details), and the values are list of
        the predictoins corresponding to the anomaly list. This list only
        contains True and/or False, True indicates a prediction.
    """
    predictions = {}
    # log_file and refresh
    prediction_logfile = localizer_config.get_dst_path('predictions.txt')
    with open(prediction_logfile, 'w') as f:
        f.write('')

    training_cache = localizer_config.load_cache('predictions', 'training')
    validation_cache = localizer_config.load_cache('predictions', 'validation')
    target_cache = localizer_config.load_cache('predictions', 'target')

    # Cache not complete. Re-train.
    if not training_cache or\
            not validation_cache or\
            not target_cache:
        predictor_name = config.get('predictor', 'predictor')
        predictor = localizer_config.get_plugin('predictor', predictor_name)

        training_data = fmtinput.fmt_folder('training')
        training_samples = [line.data for line in training_data]
        training_labels = [line.exp_obj.exp_info['faulty']
                           for line in training_data]
        predictor.train(training_samples, training_labels)

    # Training Results
    if not training_cache:
        training_predictions = process_data(predictor, training_data)
        localizer_config.save_cache(training_predictions,
                                    'predictions', 'training')
    else:
        training_predictions = training_cache
    log_predictions('TRAINING', training_predictions, prediction_logfile)
    predictions.update(training_predictions)

    # Validation Results
    if not validation_cache:
        validation_data = fmtinput.fmt_folder('validation')
        validation_predictions = process_data(predictor, validation_data)
        localizer_config.save_cache(validation_predictions,
                                    'predictions', 'validation')
    else:
        validation_predictions = validation_cache
    predictions.update(validation_predictions)
    log_predictions('VALIDATION', validation_predictions, prediction_logfile)

    # Target Results
    if not target_cache:
        target_data = fmtinput.fmt_folder('target')
        target_predictions = process_data(predictor, target_data)
        localizer_config.save_cache(target_predictions,
                                    'predictions', 'target')
    else:
        target_predictions = target_cache
    predictions.update(target_predictions)
    log_predictions('TARGET', target_predictions, prediction_logfile)

    return predictions


def process_data(predictor, dataset):
    """Extract the input data and make a prediction.

    Args:
        predictor(obj): an implementation of plugin.predictor.general_predictor
        dataset(list): a list of util.fmtinput.PredData object

    Returns:
        A dictionary where the keys are the indices of the experiments(see
        util.runtime.Observation for more details), and the values are list of
        the predictoins corresponding to the anomaly list. This list only
        contains True and/or False, True indicates a prediction.
    """
    anomaly_data = [x.data for x in dataset]
    predictor_output = predictor.predict(anomaly_data)
    predictions = {}
    for i, data in enumerate(dataset):
        exp_id = data.exp_obj.exp_info['id']
        if exp_id not in predictions:
            predictions[exp_id] = []
        predictions[exp_id].append(predictor_output[i])

    return predictions


def log_predictions(label, predictions, dst):
    """Write the result of the predictions to some files.

    The file will contain the prediction of each experiment, and a total
    statistics of the dataset.

    Args:
        label(str): A one-word desctription of the data set.
        predictions(dict): The prediction results, which is a dictionary where
            the keys are the indices of the experiments(see
            util.runtime.Observation for more details), and the values are list
            of the predictoins corresponding to the anomaly list. This list
            only contains True and/or False, True indicates a prediction.
        dst(str): The file to write the results.

    Returns:
        None
    """
    import util.runtime as runtime
    exps = runtime.all_exps
    with open(dst, 'a') as f:
        for idx, prediction in predictions.items():
            if idx in exps:
                exp = exps[idx]
                line = ('[experiment: {idx}][{rsc}:{typ}]'
                        'Prediction: {prediction}\n')\
                    .format(idx=exp.exp_info['id'],
                            rsc=exp.exp_info['faulty_resource'].rjust(10),
                            typ=exp.exp_info['fault_type'].rjust(10),
                            prediction=str(prediction))
                f.write(line)
            else:
                localizer_log.error("Experiment {exp_idx} not loaded!"
                                    .format(exp_idx=idx))

    result = stat(predictions)
    localizer_log.stdout(('{labl}: {instance} instances, '
                          '{correct} correct predictions, '
                          '{rate}% rate')
                         .format(labl=label,
                                 instance=str(result[0]),
                                 correct=str(result[1]),
                                 rate=str(result[2])))


def stat(predictions):
    """Compute the statistic results.

    The main measurements are the number and percentage of experiments that are
    correctly predicted.

    Args:
        predictions(dict): The prediction results, which is a dictionary where
            the keys are the indices of the experiments(see
            util.runtime.Observation for more details), and the values are list
            of the predictoins corresponding to the anomaly list. This list
            only contains True and/or False, True indicates a prediction.
    Returns:
        A tuple that contains:
        - Total number of experiments
        - Number of experiments that are correctly predicted
        - Pecentage of experiments that are correctly predicted
    """
    import util.runtime as runtime
    exps = runtime.all_exps

    correct = 0
    total = 0
    for idx, prediction in predictions.items():
        total += 1
        faulty = exps[idx].exp_info['faulty']
        pred, t = check_stable_prediction(prediction)
        if pred is faulty:
            correct += 1

    return (total, correct, float(correct)/total*100)


def check_stable_prediction(prediction):
    """Check if a prediction sequence is stably giving predictions.

    If there are a continuous number of True values in the given sequence, it
    will be identify as stable prediction. This number is defined in
    '[predictor]/<stable_prediction>' in the config file.
    
    Args:
        prediction(list): A list representing the predictoins of an experiment
            corresponding to the anomaly list. This list only contains True
            and/or False, True indicates a prediction.

    Returns:
        A tuple that contains:
        - A boolean that indicates if there is a stable prediction.
        - An integer that indicates the time of the stable prediction if there
        is one, otherwise 0.
    """
    stable_pred = config.getint('predictor', 'stable_prediction')
    local_cnt = 0
    for i, pred in enumerate(prediction):
        if pred is False:
            local_cnt = 0
        else:
            local_cnt += 1
            if local_cnt > stable_pred:
                return True, i
    return False, 0


if __name__ == '__main__':
    run()
