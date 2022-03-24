# AnomalyRanker

## Table of Contents
1. [Introduction](#introduction)
2. [Environment](#environment)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [Write your own plugin](#write-your-own-plugin)
6. [Notes](#Notes)

AnomalyRanker is a framework for fault localization. It reads 

- Sets of anomalous KPIs(Key Performance Indicators, i.e., (resource name, metric name) pairs such as (machine1, CPU_usage),
- A file that contains the name and indices of thhe KPIs, and
- A graph that represents the relationships between KPIs

as input and produce a culprit resource that may be the faulty resource.

## Introduction

AnomalyRanker reads time series anomalous KPIs (i.e. anomalies), predicts potential failure and localize faulty resources. It now works online with RESTful APIs.

The *offline* mode works with pre-generated files, basically in the following steps:

- *Training*. Using json file intputs which contain list of anomaly sets under normal condition, AnomalyRanker is able to train it self and produce a model ready to predict failures.
- *Predict*. By reading the json files which contains the anomaly sets at different timestamp, the predictor will give a *failure prediction* on each of them, which indicates that the system may suffer a potential failure.
- *Rank*. The localizer takes the anomaly sets at different timestamps and a graph with its weights representing the relationships between KPIs, and produces rankings of the KPIs.
- *Verify*. The verifier selects a timestamp, picks the rankings of KPIs at that timestamp, and determines the resource that is most likely the faulty one. Under offline mode, if the faulty resource is already know, the verifier will check if its verification is correct.

Some features, such as *Predict*, *Rank*, and *Verify*, are configurable. Users can write their own implementation as plugins.

## Environment

A machine with Ubuntu 14.04 or other Linux-based/POSIX system installed is required. Packages needed are written in ```ubuntu_req.txt```. You can use ```apt-get``` in ubuntu or other package manager in other operating systems to install them.

Python version 3.6 is also required. Some external libraries are needed to run AnomalyRanker, and you can installed them by:

```
pip3 install -r requirements.txt
```

## Quick Start

#### Docker

Run

```bash
docker-compose up -d
```

#### Server Side

Simply run

```
python3 ranker_app.py
```

will make the server run. You can also make it a system service modifying the ```RESTful/anomalyranker``` file according to your system settings and putting it as a service(i.e under ```/etc/init.d/```) then start it(i.e. ```service anomalyranker start```.

#### Client Side
The RESTful API provides several features:

1. **Reset all settings** by clearing up kpi list, gml model and predictor model: Send a POST request to /reset with a json. Example json:

    ```
    {
        "reset": true
    }
    ```
    There will be a 200 response if succeed. Or the server will send a 500 return code if the request is not in correct format.

1. **Update kpi list**: Send a POST request to /update_kpi with a json. Example json:
        
    ```
    {
        "kpis": ${LIST OF KPI}
    }
    ```
    
    A "KPI" here represents a KPI item, which is in the form like:
    
    ```
    {
	  timestamp: [long] Timestamp in milliseconds,
	  resource: [Resource] Resource of the KPI,
	  metric: [Metric] Metric of the KPI,
	  value: [double] Value of the KPI
	}

    ```
    Here is a sample of a simple KPI:
    
    ```
	{
	  "timestamp":1522751098000,
	  "resource":{
	    "name":"Node2"
	  },
	  "metric":{
	    "name":"MEMORY"
	  },
	  "value":48928.6
	}
	```
    
    There will be a 200 response if succeed. Or the server will send a 500 return code if the request is not in correct format.
  	
1. **Update gml graph**: Send a POST request to /update_gml with a json. Requires *update\_kpi* to be done first. Example json:

    ```
    {
        'gml': ${PLAIN_TEXT_OF_THE_GML_FILE}
    }
    ```
    There will be a 200 response if succeed. Or the server will send a 500 return code if the request is not in correct format or prerequisites are not satisfied.

1. **Training**: Send a POST request to /train with a json. Requires *update_kpi* to be done first. Example json:
	
    ```
    {
        'training': [${LIST_1}, ${LIST_2}, ${LIST_3} ...]
    }
    ```
    in which each list contains the KPI items of the anomalies.
    
	 There will be a 200 response if succeed. Or the server will send a 500 return code if the request is not in correct format or prerequisites are not satisfied.
	  	
1. **Prediction**: Send a POST request to /predict with a json. Requires *train* to be done first. Example json:
	
    ```
    {
        'anomalies': [${KPI1}, ${KPI2}, ${KPI3} ...]
    }
    ```
    in which the KPI representation of the anomalies are put.
	 The server will return a json in the form like:
  
    ```
    {
        'prediction': True
    }
    ```
    In which True means a failure alert or False means normal. Or the server will send a 500 return code if the request is not in correct format or prerequisites are not satisfied.
	  		
1. **Localization**: Send a POST request to /localize with a json. Requires *update_kpi* and *update_gml* to be done first.
	
    ```
    {
        'anomalies': [${KPI1}, ${KPI2}, ${KPI3} ...]
    }
    ```
    in which the KPI representation of the anomalies are put.
    The server will return a json in the form like:
	  	
    ```
    {
        'suspected_list': [[${RSC1}, ${RANKING SCORE 1}], [${RSC2}, ${RANKING SCORE 2}], ...], 'localization': {RSC}
    }
    ```
	  In which suspected_list includes the resources and their ranking scores, and localization indicates the faulty resource. Or the server will send a 500 return code if the request is not in correct format (e.g. empty json)

### Testing

We also provie some basic tests that covers the necessary scenarios. To run it, check the json files under ```RESTful/tests``` and run at the root directory:

```
python RESTful/client_test.py
```

or you can run the different types of tests respectively:
  
```
python RESTful/client_test.py ${TEST_CASE_NAME}
```
  
In which ```${TEST_CASE_NAME}``` refers to the json file under ```RESTful/tests```.

You can also write your own test cases, by adding a json file under ```RESTful/tests```, which contains an array of objects, each object represnets a single scenario request and includes three keys:

- *api*: name of the RESTful API to request;
- *scenario*: the json to send in the POST request. These scenarios are placed under ```RESTful/scenarios/${api}/```. You can also write your own ones.
- *expected_code*: the expected return code of this request. If all return codes of the requests in a test match their expected codes, the test will be passed. 

## Configuration

To set up the configuration, create a ```config``` file. We provide you a sample (i.e. ```config.sample```) for refering. The meanings of the options are as follows:

- [default]
	- *\<debug\>* Whether dubug messages are logged or not. ```true``` indicates it is on.
 
- [predictor]
	- *\<predictor\>* The module and class of the predictor to be used under ```plugins/predictor```.
	- *\<stable_prediction\>* When 'faulty' predictions are observed in a row for a given number of windows, a prediction is confirmed. This option specifies the length of windows.

- [ranker] 
	- *\<rankers\>* Module name and class names of the ranker under ```ranker/```, like ```centrality_ranker.CentralityRanker```. Seperated by ```,```.
	- *\<ranking_top\>*,*\<ranking_size\>* If *\<ranking_top\>* is set to ```true```, AnomalyRanker will only generate top *\<ranking_size\>* ranking KPIs at each timestamp.

- [ranking_filter]
	- *\<filter\>* The module and class of the ranking filter to select. We provide some filters to allow to filter out some of the rankings. Filter classes are under ```plugins/ranking_filter/```. Other options in this section are corresponding to the settings of the filter, and you can refer to the filter's docstrings under ```plugins/ranking_filter``` for details.
	
- [oracle]
	- *\<oracle\>* The module and class of the oracle to select. We provide some oracles to verify of the rankings. Filter classes are under ```plugins/oracle/```. Other options in this section are corresponding to the settings of the oracle, and you can refer to the oracle's docstrings under ```plugins/oracle``` for details.

- [restful]
	- *\<test_url\>* URL that the client uses to access the RESTful service. Used for testing.
	- *\<service_port\>* The port number that the server uses to provide the service.
	- *\<predictor\>*, *\<ranker\>*, *\<oracle\>* The module and class name of respective compoents uesed.
	- *\<cached\>* Wheter or not to cache the kpi list, gml model and predictor in terms of service restart.
	- *\<cached_dir\>* The folder to place cache data
	- *\<kpi_cached\>*, *\<gml_cached\>*, *\<pred_cached\>* The filenames of the kpi list/gml models/predictor to cache.
	- *\<log_file\>* The path to put the log file.
	- *\<logfile_backups\>* The number of log files to backup. Default to 10.
	- *\<logfile_size\>* If the size(e.g '1K', '20KB', '10M') is excceeded, the current log file will be backuped, and the following logs to a new empty log file.
	
## Write your own plugin

You can also write you own plugins by adding a module under ```plugins/${plugin_type}/```, and inside it create a class which should be a subclass of ```plugins/${plugin_type}/general_*```.


## Notes

If *cached*, *cached_dir*, *pred_cached* is provied under section [restful], you will find the predictor model under the specified directory after the first training. This enables model migration.
