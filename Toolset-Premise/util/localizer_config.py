# -*- coding: utf-8 -*-
"""Centralized config parser. Loads the global config file as the runtime
settings.

Attributes:
    config(object): The configparser object from the 'config' file.
    rest_mode(boolean): The boolean that indicates if the program is running on
        online rest mode or offline mode.
"""
import configparser
import shutil
import os
import pickle
from importlib import import_module
import util.localizer_log as localizer_log
import weka.core.serialization as serialization
from weka.classifiers import Classifier
from weka.core.dataset import Instances

config = configparser.RawConfigParser()
rest_mode = False
config.optionxform = str

if os.path.isfile('config.ini'):
    config.read('config.ini')


def load(filename):
    """Load/Reload config file which is organized in the .ini format and
    contains the global settings. See README and config.sample for reference.

    Args:
        filename(str): The config file to read.

    Returns:
        None
    """
    global config
    if os.path.isfile(filename):
        config.read(filename)
    else:
        localizer_log.error("Config file {fname} not found"
                            .format(fname=filename))


def get_folder(target):
    """Get the path of the folder under root directory.

    The folder name should be defined in the config file. See README and
    config.sample for reference.

    Args:
        target(str): The option name defined in '[folder]' section in the
            config file. The value of the option should be the folder name to
            read.

    Returns:
        The path of the target folder.
    """
    global config
    if not config.has_section('folder') or \
            not config.has_option('folder', target):
        localizer_log.error("folder/{folder_name} option is missing!"
                            .format(folder_name=target))
    return config.get('folder', target)


def get_scapidata_path(target):
    """Get the path of the folder under the SCAPI original data directory.

    The folder name should be defined in the config file. See README and
    config.sample for reference.
    If the folder is not found, it will issue an error and quit.

    Args:
        target(str): The option name defined in '[folder]' section in the
            config file. The value of the option should be the folder name to
            read.

    Returns:
        The path of the target folder.
    """
    global config
    if not config.has_section('folder') or \
            not config.has_option('folder', 'preprocess'):
        localizer_log.error("folder/preprocess option is missing!")
    scapi_folder = config.get('folder', 'preprocess')
    return get_joint_path(scapi_folder, target)


def get_meta_path(target):
    """Get the path of the file under the meta data directory.

    The file name should be defined in the config file. See README and
    config.sample for reference.
    If the file is not found, it will issue an error and quit.

    Args:
        target(str): The option name defined in '[meta]' section in the
            config file. The value of the option should be the folder name to
            read.

    Returns:
        The path of the target file.
    """
    global config
    if not config.has_section('folder') or not config.has_option('folder', 'meta'):
        localizer_log.error("folder/meta option is missing!")
    if not config.has_section('meta') or not config.has_option('meta', target):
        localizer_log.error("{option} option is missing!"
                            .format(option='meta/' + str(target)))
    meta_folder = config.get('folder', 'meta')
    f_name = config.get('meta', target)
    return get_joint_path(meta_folder, f_name)


def get_src_path(target):
    """Get the path of the folder under the source data directory.

    The folder name should be defined in the config file. See README and
    config.sample for reference.
    If the folder is not found, it will issue an error and quit.

    Args:
        target(str): The option name defined in '[folder]' section in the
            config file. The value of the option should be the folder name to
            read.

    Returns:
        The path of the target folder.
    """
    global config
    if not config.has_section('folder') or \
            not config.has_option('folder', 'src'):
        localizer_log.error("folder/src option is missing!")
    if not config.has_option('folder', target):
        localizer_log.error("{option} option is missing!"
                            .format(option='folder/' + str(target)))
    src_folder = config.get('folder', 'src')
    folder = config.get('folder', target)
    return get_joint_path(src_folder, folder)


def get_dst_path(target):
    """Get the path of the folder under the destination data directory.

    The folder name should be defined in the config file. See README and
    config.sample for reference.

    Args:
        target(str): The option name defined in '[folder]' section in the
            config file. The value of the option should be the folder name to
            read.

    Returns:
        The path of the target folder.
    """
    global config
    if not config.has_section('folder') or not config.has_option('folder', 'dst'):
        localizer_log.error("folder/dst option is missing!")
    dst = config.get('folder', 'dst')

    return os.path.join(dst, target)


def get_joint_path(folder, target):
    """Get the file/folder joint by the two parts(a folder and a target).

    If the file/folder is not found, it will issue an error and quit.

    Args:
        folder(str): The name of the file/folder.

    Returns:
        The path of the target file/folder.
    """
    if not folder or not target:
        localizer_log.error("Parameter cannot be empty!")

    path = os.path.join(folder, target)
    if not os.path.exists(path):
        localizer_log.error("Path {fname} not found! Abort.".format(fname=target))
    return path


def component_enabled(component):
    """Check if a given component is enabled

    The components should be defined in the config file. See README and
    config.sample for reference.

    Args:
        component(str): The name of the component.

    Returns:
        True if the component is enabled, otherwise False.
    """
    global config
    if config.has_section('component') and\
            config.has_option('component', component):
        return config.getboolean('component', component)
    else:
        return False


def reset_path(path):
    """Create a folder. If the folder exists, clears what it contained.

    Args:
        path(stt): The path of the folder.

    Returns:
        None
    """
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)


def build_if_not_exist(path):
    """Create a folder, if the folder does not exsit.

    Args:
        path(stt): The path of the folder.

    Returns:
        None
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def cache_enabled(target):
    """Check if the target caching is enabled.

    If cache feature is enabled and cache files are found, the target caching
    is considered as enabled.
    The caches should be defined in the config file. See README and
    config.sample for reference.

    Args:
        target(str): The target option in '[cached]' section in the config
            file.

    Returns:
        True if the target caching is enabled, otherwise False.
    """
    global config
    global rest_mode

    if rest_mode:
        return False

    option = target + '_cached'
    if config.has_section('cached') and \
            config.has_option('cached', option):
        return config.getboolean('cached', option)
    else:
        return False


def save_cache(obj, target, filename):
    """Save the object to the target caching file.

    The caches should be defined in the config file. See README and
    config.sample for reference.

    Args:
        target(str): The target option in '[cached]' section in the config
            file.

    Returns:
        True if the target caching is saved, otherwise False.
    """
    if rest_mode:
        return

    folder = os.path.join('caches', target)
    path = os.path.join(folder, filename + '.cache')
    build_if_not_exist(folder)
    with open(path, 'wb') as f:
        pickle.dump(obj, f)
        localizer_log.msg("Saved cache of {target_name}."
                          .format(target_name=target))
    return True


def load_cache(target, filename):
    """Load the object from the target caching file.

    The caches should be defined in the config file. See README and
    config.sample for reference.

    Args:
        target(str): The target option in '[cached]' section in the config
            file.

    Returns:
        The object if the target caching is saved, otherwise None.
    """
    if rest_mode:
        return None

    folder = os.path.join('caches', target)
    path = os.path.join(folder, filename + '.cache')
    print("cache path", path)
    if not cache_enabled(target):
        localizer_log.msg("Cache not enabled for {target_name}."
                          .format(target_name=target))
        return None

    if os.path.isfile(path):
        with open(path, 'rb') as f:
            obj = pickle.load(f)
            localizer_log.msg("Loaded cache {fname} of {target_name}."
                              .format(fname=filename, target_name=target))
        return obj

    localizer_log.msg("Failed to load cache of {target_name}."
                      .format(target_name=target))
    return None


def save_model(model, data, filename):
    """Save the model to the target caching file.

    The caches should be defined in the config file. See README and
    config.sample for reference.

    Args:
        model(obj): The model to be saved. Should be a
            weka.classifier.Classifier object.
        data(obj): The training set to be cached.
        target(str): The target option in '[cached]' section in the config
            file.
        filename(str): The target file to save.

    Returns:
        True if the target caching is saved, otherwise False.
    """

    folder = os.path.join('caches', 'model')
    path = os.path.join(folder, filename + '.cache')
    build_if_not_exist(folder)
    serialization.write_all(path, [model, Instances.template_instances(data)])
    localizer_log.msg("Saved cache of {target_name}.".format(target_name='model'))
    return True


def load_model(filename):
    """ Load the model from cache.
    Args:
        filename(str): The target file name (without extension) to load. Example: LMT
    Returns:
        The classifier and data object if the target caching is saved, otherwise None.
    """

    # Path to the cashed model (example: caches/model/LMT.cache)
    path = os.path.join(os.path.join('caches', 'model'), filename + '.cache')

    print("Path to the cashed model to load:", path)

    if os.path.isfile(path):
        cached_model, cached_data_used_for_training = serialization.read_all(path)
        print("Loading cached classifier")
        trained_classifier = Classifier(jobject=cached_model)
        print("Loading cached data")
        training_data = Instances(jobject=cached_data_used_for_training)
        localizer_log.msg("Loaded model: {filename}".format(filename=filename))
        return [trained_classifier, training_data]

    localizer_log.msg("Failed to load cache of 'model'.")
    return None


def get_klass(module_name, klass_name):
    """Get a class by reflection.

    Args:
        module_name(str): Name of the module.
        klass_name(str): Name of the class in the module.

    Returns:
        The target class.
    """
    module = import_module(module_name)
    klass = getattr(module, klass_name)

    return klass


def get_plugin(plugin_type, klass_full):
    """Get a plugin class by reflection.

    Plugins are put under plugins. Different types are put in different folder.
    See README for more information.

    Args:
        plugin_type(str): Name of the type of the plugin.
        klass_name(str): Module and class name of the target, in the form of
            ${Module Name}.${Class Name}

    Returns:
        The target class of the plugin.
    """
    SUPER_CLASSES = {'predictor': 'general_predictor.GeneralPredictor',
                     'exp_filter': 'general_expfilter.GeneralExpFilter',
                     'exp_tag': 'general_exptag.GeneralExpTag',
                     'denoiser': 'general_denoiser.GeneralDenoiser',
                     'kpi_filter': 'general_kpifilter.GeneralKPIFilter',
                     'rankingtime': 'general_selector.GeneralSelector',
                     'ranker': 'general_ranker.GeneralRanker',
                     'oracle': 'general_oracle.GeneralOracle'}
    PLUGIN_DIR = 'plugins'

    klass_terms = klass_full.strip().split('.')
    module_name = '.'.join(klass_terms[:-1])
    klass_name = klass_terms[-1]
    plugin_klass = get_klass('.'.join([PLUGIN_DIR,
                                       plugin_type,
                                       module_name]),
                             klass_name)

    if plugin_type in SUPER_CLASSES:
        superclass_full = SUPER_CLASSES[plugin_type]
        superklass_terms = superclass_full.split('.')
        superklass_module = '.'.join(superklass_terms[:-1])
        superklass_name = superklass_terms[-1]
        super_klass = get_klass('.'.join([PLUGIN_DIR,
                                          plugin_type,
                                          superklass_module]),
                                superklass_name)
        if not issubclass(plugin_klass, super_klass):
            localizer_log.error("{subclass} should inherit {superclass}"
                                .format(subclass=klass_full,
                                        superclass=superclass_full))

    return plugin_klass
