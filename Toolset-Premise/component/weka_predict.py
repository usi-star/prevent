"""Core module of the premise prediction."""
import re
import os
import json
from collections import OrderedDict
import util.localizer_config as localizer_config
import util.localizer_log as localizer_log

import weka.core.converters as converters
from weka.classifiers import Classifier
from weka.classifiers import Evaluation
from weka.core.classes import Random


if os.path.isfile('weka.json'):
    with open('weka.json') as f:
        try:
            __OPTIONS = json.load(f)
        except:
            localizer_log.error('weka.json not in right format.')
            __OPTIONS = []
else:
    localizer_log.error('weka.json not found.')
__classifiers = OrderedDict(__OPTIONS)
__predictors = {}


def load_model(model_cache_file_name):
    """ Loads the cached classifier model and writes it to the __predictors global variable
    :param model_cache_file_name: path of the classifier model file
    :return: N/A
    """
    global __predictors
    # __predictors[classifier_name], data = localizer_config.load_model(classifier_name)
    path = os.path.join('caches', 'model')
    path = os.path.join(path, model_cache_file_name + '.cache')
    __predictors["LMT"], _ = Classifier.deserialize(path)


def train(training_dataset_path, model_cache_file_name, evaluation_is_on, summary_file_path):
    """Model Training function

    The function uses the WEKA machine learning library, implemented by
    python-weka-wrapper Python library. Divides the data into given
    folds, and do the training and evaluation. Trained model copied to __predictors global variable
    and also saved (together with training data set) to the model_cache_file_name file. Evaluation summary is being written to summary_file_path file.

    Args:
        :param training_dataset_path: the path of the input arff file.
        :param model_cache_file_name:
        :param evaluation_is_on: run evaluation after training (true / false)
        :param summary_file_path: the path of the model evaluation summary file.

    Returns:
        None
    """

    global __classifiers
    global __predictors

    training_data = converters.load_any_file(training_dataset_path)
    training_data.class_is_last()

    lines = []
    summaries = []
    summary_line = ['Model'.ljust(16),
                    'Precision'.ljust(12),
                    'Recall'.ljust(12),
                    'F-measure'.ljust(12),
                    'Accuracy'.ljust(12),
                    'FPR'.ljust(12)]
    summaries.append('\t'.join(summary_line))

    for classifier, option_str in __classifiers.items():
        option_list = re.findall(r'"(?:[^"]+)"|(?:[^ ]+)', option_str)
        option_list = [s.replace('"', '') for s in option_list]

        classifier_name = classifier.split('.')[-1]
        info_str = "Using classifier: {classifier}, options: {options}".format(classifier=classifier_name, options=str(option_list))
        localizer_log.msg(info_str)
        lines.append(info_str)

        # Train
        cls = Classifier(classname=classifier, options=option_list)
        localizer_log.msg("Start building classifier")
        cls.build_classifier(training_data)
        localizer_log.msg("Completed building classifier")
        localizer_log.msg("Saving trained model to {model_cache_name}".format(model_cache_name=model_cache_file_name))

        # localizer_config.save_model(cls, training_data, model_cache_file_name)
        path = os.path.join('caches', 'model')
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        path = os.path.join(path, model_cache_file_name + '.cache')
        cls.serialize(path)
        localizer_log.msg("Trained model saved")

        classifier2, _ = Classifier.deserialize(path)
        print(classifier2)

        __predictors[classifier_name] = cls

        if evaluation_is_on:

            # Model evaluation
            localizer_log.msg("Start evaluation classifier")
            evl = Evaluation(training_data)
            localizer_log.msg("Complete evaluation classifier")

            localizer_log.msg("Start cross-validating classifier")
            evl.crossvalidate_model(cls, training_data, 10, Random(1))
            localizer_log.msg("Complete cross-validating classifier")

            # print(evl.percent_correct)
            # print(evl.summary())
            # print(evl.class_details())

            lines.append(evl.summary())
            lines.append(evl.class_details())

            summary_line = []
            summary_line.append(classifier_name.ljust(16))
            summary_line.append("{:.3f}".format(evl.weighted_precision * 100).ljust(12))
            summary_line.append("{:.3f}".format(evl.weighted_recall * 100).ljust(12))
            summary_line.append("{:.3f}".format(evl.weighted_f_measure * 100).ljust(12))
            summary_line.append("{:.3f}".format(evl.percent_correct).ljust(12))
            summary_line.append("{:.3f}".format(evl.weighted_false_positive_rate * 100).ljust(12))
            summaries.append('\t'.join(summary_line))

            # Save evaluation summary to file
            with open(summary_file_path, 'w') as f:
                f.writelines('\n'.join(lines))
                f.writelines('\n'*5)
                f.writelines('\n'.join(summaries))


def predict(exp, arff_path, dst_folder):
    """The function to generate a detailed prediction sequence of the experiment.

    Args:
        exp(obj): An util.runtime.Observation object.
        arff_path(str): The string that represents the path of the input arff
            file.
        dst_folder(str): The path of the folder to put the result.

    Returns:
        None
    """
    global __predictors
    import util.runtime as runtime
    import weka.core.converters as converters

    data = converters.load_any_file(arff_path)
    data.class_is_last()
    for cls_name, cls in __predictors.items():
        f_path = os.path.join(dst_folder, cls_name + '.txt')
        with open(f_path, 'w') as f:
            lines = []
            for index, inst in enumerate(data):
                prediction = cls.classify_instance(inst)
                print("Predictions file:", f_path, "Prediction:", prediction, "[", int(prediction), "]", runtime.all_classes[int(prediction)])
                # print("runtime.all_classes:", runtime.all_classes)
                lines.append(runtime.all_classes[int(prediction)])
            f.writelines('\n'.join(lines))


def check_stable_prediction(prediction):
    """Remains compatibility with ranker code.

    Args
        prediction(list): A list of True and/or False.

    Returns:
        None
    """
    pass
