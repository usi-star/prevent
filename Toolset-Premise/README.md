# Premise Failure Predictor

## Table of Contents
1. [Introduction](#introduction)
2. [Envrionment](#environment)
3. [Quick Start](#quick-start)
4. [Congfiguration](#configuration)
5. [Write your own plugin](#write-your-own-plugin)

Premise is a framework using different types of supervised machine learning techniques to predict failures. It reads 

- Sets of anomalous KPIs(Key Performance Indicators, i.e., (resource name, metric name) pairs such as (machine1, CPU_usage),
- A file that contains the name and indices of the KPIs

as input and produce predictions on the inputs.

## Introduction

Premise reads time series anomalous KPIs (i.e. anomalies), predicts potential failure. It uses [WEKA](http://www.cs.waikato.ac.nz/ml/weka/) as the machine learnin librarey, implemented in Python with the [python-weka-wrapper3](https://pypi.python.org/pypi/python-weka-wrapper3) library. It works with pre-generated files, basically in the following steps:

- *Preprocess*. We adopt [IBM Predictive Insights](http://www-03.ibm.com/software/products/en/ibm-operations-analytics---predictive-insights) as the anomaly detector to read system numeric metric values and identify whether or not they are anomalous. This step converts the output of IBM Predictive Insights(i.e. log files) to some easy-to-read files.
- *Predict*. By reading the files which contains the anomaly sets at different timestamp, the predictor will give a *failure prediction* on each of them, which indicates that the system may suffer a potential failure.

## Environment

A machine with Ubuntu 14.04 or other Linux-based/POSIX system installed is required. Packages needed are written in ```ubuntu_req.txt```. You can use ```apt-get``` in ubuntu or other package manager in other operating systems to install them.

Python version 3.6 is also required. Some external libraries are needed to run Premise, and you can installed them by:

```
pip3 install -r requirements.txt
```

The *javabridge* library may have some problems installing from pypi, thus we recommend you to install from github:

```
pip install git+https://github.com/LeeKamentsky/python-javabridge.git
```

## Quick Start

Before running, you need to [set the configuration](#configuration), and prepare a meta file, which is:

- A txt file which contains the KPI indices(i.e. GCD numbers), resources, metric names and groups, in the format of [IBM Predictive Insights](http://www-03.ibm.com/software/products/en/ibm-operations-analytics---predictive-insights) output logs, i.e. the file with the name granger_\*.json.\*.txt

We provide the meta file sample under ```meta``` folder.

### Offline Mode

There are two ways to prepare the offline input data:

- You can get the anoamlies log files produced by [IBM Predictive Insights](http://www-03.ibm.com/software/products/en/ibm-operations-analytics---predictive-insights). Data for training, validation and analyzing should be put in seperated folders under ```[folder]/<preprocess>```, with each experiments a folder. Experiment folder name should follow the patter:

    ```
    ${timestamp}-${ip of the faulty resource(if not faulty, just a random ip)}-${fault type}-${faulty resource}-${fault parameter}
    ```
- You can also skip the prepocess by setting ```[component]/<preprocess>``` to ```false```, and put the anomaly files of training, validation and analyzing in seperated folders under ```[folder]/<src>```, with each experiment a subfolder. In each experiment's folder, you should place the anomalies at a timestamp in a txt file, naming the file with the timestamp in interger numer, and in each txt file put a anomaly a line, for example:

    File name: 300.txt
    
    ```
    ('bono', 'SnmpBonoGroup', 'Bonoqueuesizevariance')
	('bono', 'SnmpGeneralGroup', 'Ssrawinterrupts')
	('huawei5', 'KlzSystemStaticsGroup', 'TotalNumberProcesses')
	('bono', 'SnmpGeneralGroup', 'Sscpurawsoftirq')
	('sprout', 'SnmpSproutGroup', 'Sproutsarlatencyvariance')
	('bono', 'SnmpGeneralGroup', 'Memtotalfree')
	('sprout', 'SnmpSproutGroup', 'Sproutqueuesizelwm')
	('huawei5', 'KlzVmStatsGroup', 'SwapSpaceUsed')
	('huawei5', 'KlzSystemStaticsGroup', 'CxtSwitchesPerSec')
    ```

After all data is prepared, run:

```
python3 run.py
```

and view the results in ```[folder]/<dst>```


## Configuration

To set up the configuration, create a ```config``` file. We provide you a sample (i.e. ```config.sample```) for refering. The meanings of the options are as follows:

- [default]
	- *\<debug\>* Whether dubug messages are logged or not. ```true``` indicates it is on.
	- *\<nonfaulty_pattern\>* Under offline mode, if this pattern is found in the name of the experiment, it will be recognized as a normal execution, otherwise a faulty execution.
        - *\<max_heapsize\>* The maximun heap size of jvm (i.e. -Xmx parameter). If not set, the default value will be used.

- [folder]
	- *\<preprocess\>* The folder where all the SCAPI original log data will be put.
	- *\<src\>* The folder where all the anomaly data will be put.
	- *\<dst\>* The folder where the analyzing result will be put.
	- *\<meta\>* The folder where the meta files will be put. For more information, see section ```[meta]```
	- *\<training\>* Name of the training set folder under *\<src\>*.
	- *\<target\>* The subfolder name under *\<src_folder\>* where the experiment data that are going to be analyzed is placed.

- [meta]
	- *\<kpi\>* File name of the KPI list under folder *\<meta\>*.

- [component]
	- *\<preprocess\>* Wherther the preprocessing is turned on or not. ```true``` indicates it is on. 
	- *\<predict\>* Whether the predictor is turned on or not. ```true``` indicates it is on. For more information, see section ```[predictor]```.
	- *\<exp_filter\>* Whether to filter out some experiments or not. ```true``` indicates it is on. For more information, see section ```[exp_filter]```.

- [cached]
	- The options in this section features the caching of some data. If set to ```true```, Premise will look for caches first to avoid redundant processing.

- [preprocess]
	- *\<targets\>* the folders under *\<src_folder\>* that are going to be preprocessed, seperated by ```,```.
	- *\<anomaly_string\>* The string pattern to recognize a line in the SCAPI log file that contains the anomalies.
	- *\<log_file_name\>* Name of the file that contains the anomalies under *\<state_dir\>*.
	- *\<Fault_start\>* Start timestamp of anomalies.
 
- [predictor]
	- *\<sliding_window\>* The length of the sliding window. Premise will gather the anoamlies within a given number of timestamps, and use them to perform the prediction. 
	- *\<fold\>* The fold number that Premise will use for training and varification.

- [exp_filter]
	- *\<filter\>* The module and class of the experiment filter to select. We provide some filters to allow to select only part of the experiments to analyze. Filter classes are under ```plugins/exp_filter/```. Other options in this section are corresponding to the settings of the filter, and you can refer to the filter's docstrings under ```plugins/exp_filter``` for details.

- [exp_tag]
	- *\<tag\>* The module and class of the experiment tag generator to select. We provide some generator to produce the tag that the experiment belongs to, which the predictor will use as the class for training and prediction. Tag generator classes are under ```plugins/exp_tag/```. You can refer to the exp_tag's docstrings under ```plugins/exp_tag``` for details.

For settings of weka, you have to create a weka.json in which the classifier and options are put. We provide a weka.json.sample for reference.
	
## Write your own plugin

You can also write you own plugins by adding a module under ```plugins/${plugin_type}/```, and inside it create a class which should be a subclass of ```plugins/${plugin_type}/general_*```. And for more API documentations regrading using weka in python, please refer to [this link](http://python-weka-wrapper.readthedocs.io/en/latest/api.html)
