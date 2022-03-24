# -*- coding: utf-8 -*-
"""The main module of premise.

Example:
    $ python3 run.py
"""

import os
import sys

import weka.core.jvm as jvm
import util.localizer_log as localizer_log
import util.localizer_config as localizer_config
from util.localizer_config import config
import util.runtime as runtime
import util.kpi_info as kpi_info
import component.preprocess as preprocess
import component.arff_gen as arff_gen
import component.exp_filter_manager as exp_filter_manager
import component.weka_predict as weka_predict


def run(mode, model_cache_file_name, evaluation_is_on):
    """
    :param mode: train, predict
    :param model_cache_name: name to save the trained model (or to load the saved one). Example: LMT
    :return: N/A
    """

    if config.has_option('default', 'max_heapsize'):
        jvm.start(config.get('default', 'max_heapsize'))
    else:
        localizer_log.msg("default->max_heapsize record does not exist")
        jvm.start()

    # Create the folder (dst_folder folder) to put:
    #   1) Training data set in arff format. Example: training.arff
    #   2) Model evaluation summary. Example: predictions.txt
    #   3) Folders for each target dataset (the dataset on which classifications to be done) (example: 0000000060-10.40.7.172-PacL@Rnd_0_Rnd):
    #       3.1) Target dataset in arff format. Example: target.arff
    #       3.2) Classification results. Example: LMT.txt

    dst_folder = localizer_config.get_folder('dst')
    localizer_config.reset_path(dst_folder)

    localizer_log.msg("Initialising KPIs...")
    kpi_info.init(localizer_config.get_meta_path('kpi_indices'))
    localizer_log.msg("KPIs initialised")

    # Process the original file and put it to
    if localizer_config.component_enabled('preprocess'):
        preprocess.preprocess()

    # Add all classes to the all_classes global variable. Used in @attribute class {..} in training and target arffs.
    runtime.generate_classes_all()

    if mode == "train":

        # Reading training data from anomalies/training-data
        localizer_log.msg("Reading training data: Started.")
        training_dir = localizer_config.get_src_path('training')  # anomalies/training-data
        runtime.add_all(training_dir)
        localizer_log.msg("Reading training data: Completed.")

        if localizer_config.component_enabled('exp_filter'):
            experiments = exp_filter_manager.filter_(runtime.all_exps)
            localizer_log.msg("Exp. filter applied.")
        else:
            experiments = runtime.all_exps
            localizer_log.msg("No exp. filter applied.")

        # Generate training data set in arff format
        localizer_log.msg("Start generating the training.arff file (data for training).")
        training_dataset_arff_path = localizer_config.get_dst_path('training.arff')  # Example: data/classifications/training.arff
        arff_gen.gen_file(experiments, training_dataset_arff_path, "training", True)
        localizer_log.msg("The training.arff generated.")

        # Train
        path_to_save_training_summary = localizer_config.get_dst_path('predictions.txt')  # Example: data/classifications/predictions.txt
        weka_predict.train(training_dataset_arff_path, model_cache_file_name, evaluation_is_on, path_to_save_training_summary)

    if mode == "predict":

        # Reading training data from anomalies/test-data/
        localizer_log.msg("Reading data for classifications: Started.")
        target_dir = localizer_config.get_src_path('target')
        runtime.add_target(target_dir)
        localizer_log.msg("Reading data for classifications: Completed.")

        # Load cached model
        localizer_log.msg("Load model " + model_cache_file_name)
        weka_predict.load_model(model_cache_file_name)

        # Predict
        for exp_id, exp in runtime.targets_exps.items():
            exp_dst_path = localizer_config.get_dst_path(exp.exp_info['full_name'])
            localizer_config.reset_path(exp_dst_path)

            # Generate the target data set for predictions
            localizer_log.msg("Start generating the target.arff file (data for training).")
            exp_arff_path = os.path.join(exp_dst_path, 'target.arff')
            localizer_log.msg("target.arff file path: " + exp_arff_path)
            arff_gen.gen_file({exp_id: exp}, exp_arff_path, "test", fromzero=True)
            localizer_log.msg("The " + exp_arff_path + " generated.")

            # Make predictions
            localizer_log.msg("Start prediction.")
            weka_predict.predict(exp, exp_arff_path, exp_dst_path)
            localizer_log.msg("Prediction completed.")

    jvm.stop()


if __name__ == '__main__':
    mode = sys.argv[1]
    model_cache_file_name = sys.argv[2]
    evaluation_is_on = bool(int(sys.argv[3]))

    run(mode, model_cache_file_name, evaluation_is_on)
