# Replicated Computational Results (RCR) Report for PREVENT: An Unsupervised Approach to Predict Software Failures in Production, Giovanni Denaro, Rahim Heydarov, Ali Mohebbi, Mauro Pezzè, submitted to IEEE TSE, February 2022

## Getting Started
---

<br/>
This artifact includes  

1. **a large dataset of KPIs** (values of metrics collected from different nodes) that we obtained by running a large set of experiments on [**REDIS**](https://redis.io/), a commercially compliant, distributed cloud system. 
2. **the results of experimenting with Prevent [1], Premise [2], and Loud [3]**, three tools for predicting and localizing failures in multi-tier distributed systems, to comparatively evaluate their performance to predict and localize failures in dynamic systems.
3. **toolset to execute Prevent [1], Premise [2], and Loud [3]** in order to replicate our results (point 2 above) based on provided dataset of KPIs (point 1 above).

**Prevent** combines two approaches, **PREVENT-A** and **PREVENT-E**, that offer complementary implementations of state classifiers to predict failures, both integrated with the same anomaly ranker, **Loud**, to localize faults. 

The experiments compare:

* **Prevent** with **Premise** in terms of

    * **stability**: rate of predictions between the ﬁrst valid prediction and the system crash 
    * **reliability**: rate of predictions before the injection of the failure  
    * **earliness**: time interval between the ﬁrst valid prediction and the system crash 
    
* **Prevent** with **Loud** in terms of false-positive rate

<br/>
<br/>

## Terminology
---

* **KPI**: Key Performance Indicator, a pair of metrics, node values observed by monitoring the target application.
* **State Classifier**: the **Prevent component** that predicts failures based on the analysis of the KPIs.
* **Anomaly Ranker**: the **Prevent and Loud component** that locates the sources of the failure propagation by statistically testing the relations between the KPIs.
* **Deep Autoencoder**: the **Prevent State Classifier sub-component and a sub-component of Anomaly Ranker** that detects anomalous KPIs (concerning the observations in the training phase) in the observed data.
* **Granger Causality Analyzer**: the sub-component of the **Anomaly Ranker**, which conducts a Granger Causality analysis by building a causality graph representing the KPIs' causal dependencies.
* **OCSVM Classifier**: **Prevent State Classifier sub-component** which represents a one-class-support-vector-machine (OCSVM) classiﬁer that discriminates between benign sets of anomalies (which resemble combinations of anomalies occasionally observed during training) and failure-prone sets of anomalies.
* **master-slave pair** - a pair of master and slave nodes of the target application (Redis cluster). In our experiments, we used a cluster consisting of 10 master-slave pairs.

<br/>
<br/>

## Data: Dataset and Results
---
<br/>

## Naming Conventions

The flies contains a dataset corresponding to normal and faulty executions. Naming convention:

* e1 == Memory Leaks injected with Exponential pattern
* e2 == Memory Leaks injected with Linear pattern
* e3 == Memory Leaks injected with Random pattern
* e4 == Packet Loss injected with Linear pattern
* e5 == Packet Loss injected with Exponential pattern
* e6 == Packet Loss injected with Random pattern
* e7 == CPU Hog injected with Exponential pattern
* e8 == CPU Hog injected with Linear pattern
* e9 == CPU Hog injected with Random pattern
* normal_w1 == data collected during a week of normal execution, that is, without injected faults
* normal_w2 == data collected during a week of normal execution, that is, without injected faults
* normal_w1_2 == sequential composition of normal_w1 and normal_w2
* normal_w3 == data collected during a week of normal execution, that is, without injected faults

##  Files

* **Datasets-Raw.zip**: set of KPI values obtained by monitoring the target application (Redis cluster) executed both in normal conditions, that is, with no failures, and in failing states, that is, with injected failures. The .zip file includes 13 .csv files with different datasets:

    * **normal_w1.csv**: KPIs collected during a week of normal execution, that is, without injected faults, with a sample rate of one sample per minute 
    * **normal_w2.csv**: KPIs collected during a week of normal execution, that is, without injected faults, with a sample rate of one sample per minute
    * **normal_w1_2.csv**: KPIs collected during two weeks of normal execution, that is, without injected faults, with a sample rate of one sample per minute
    * **normal_w3.csv**: KPIs collected during a week of normal execution, that is, without injected faults, with a sample rate of one sample per minute
    * **e1.csv** - KPIs collected during execution with  **memory leak** failures injected with an **exponential injection intensity rate**, with a sample rate of one sample per minute, up to a system crash
    * **e2.csv** - KPIs collected during execution with  **memory leak failures** injected with a **linear injection intensity rate**, with a sample rate of one sample per minute, up to a system crash
    * **e3.csv** - KPIs collected during execution with  **memory leak failures** injected with a **random injection intensity rate**, with a sample rate of one sample per minute, up to a system crash
    * **e4.csv**  - KPIs collected during execution with  **packet loss failures** injected with a **linear injection intensity rate**, with a sample rate of one sample per minute, up to a system crash
    * **e5.csv**  - KPIs collected during execution with  **packet loss failures** injected with an **exponential injection intensity rate**, with a sample rate of one sample per minute, up to a system crash
    * **e6.csv**  - KPIs collected during execution with  **packet loss failures** injected with a **random injection intensity rate**, with a sample rate of one sample per minute, up to a system crash
    * **e7.csv**  - KPIs collected during execution with  **CPU hog failures** injected with an **exponential injection intensity rate**, with a sample rate of one sample per minute, up to a system crash
    * **e8.csv**  - KPIs collected during execution with  **CPU hog failures** injected with a **linear injection intensity rate**, with a sample rate of one sample per minute, up to a system crash
    * **e9.csv**  - KPIs collected during execution with  **CPU hog failures** injected with a **random injection intensity rate**, with a sample rate of one sample per minute, up to a system crash

>These files are provided in the form of comma separated values (.csv) files, where each row corresponds to a set of KPI values collected at a timestamp:
> * Columns A: timestamp in "yyyy-mm-ddTh:m:s.000Z" format, where "000Z" is a constant. Example: 2020-4-13T19:13:00.000Z.
>   * Columns B..ZZ: KPI == values of the metrics collected at the cluster nodes; the title row provides <node, metrics> identifiers.

* **Datasets-Raw-Splitted.zip**: set of KPI values obtained by monitoring the target application (Redis cluster) executed both in normal conditions, that is, with no failures, and in failing states, that is, with injected failures. This folder contains the same data as the **Datasets-Raw.zip** does; the only difference is that the data is distributed by the folders, and each folder contains a specific dataset split to .csv files by the samples of 30 consecutive observations.

    * **normal_w1**: KPIs collected during a week of normal execution, that is, without injected faults, with a sample rate of one sample per minute 
    * **normal_w2**: KPIs collected during a week of normal execution, that is, without injected faults, with a sample rate of one sample per minute
    * **normal_w1_2**: KPIs collected during two weeks of normal execution, that is, without injected faults, with a sample rate of one sample per minute
    * **normal_w3**: KPIs collected during a week of normal execution, that is, without injected faults, with a sample rate of one sample per minute
    * **e1** - KPIs collected during execution with  **memory leak** failures injected with an **exponential injection intensity rate**, with a sample rate of one sample per minute, up to a system crash
    * **e2** - KPIs collected during execution with  **memory leak failures** injected with a **linear injection intensity rate**, with a sample rate of one sample per minute, up to a system crash
    * **e3** - KPIs collected during execution with  **memory leak failures** injected with a **random injection intensity rate**, with a sample rate of one sample per minute, up to a system crash
    * **e4**  - KPIs collected during execution with  **packet loss failures** injected with a **linear injection intensity rate**, with a sample rate of one sample per minute, up to a system crash
    * **e5**  - KPIs collected during execution with  **packet loss failures** injected with an **exponential injection intensity rate**, with a sample rate of one sample per minute, up to a system crash
    * **e6**  - KPIs collected during execution with  **packet loss failures** injected with a **random injection intensity rate**, with a sample rate of one sample per minute, up to a system crash
    * **e7**  - KPIs collected during execution with  **CPU hog failures** injected with an **exponential injection intensity rate**, with a sample rate of one sample per minute, up to a system crash
    * **e8**  - KPIs collected during execution with  **CPU hog failures** injected with a **linear injection intensity rate**, with a sample rate of one sample per minute, up to a system crash
    * **e9**  - KPIs collected during execution with  **CPU hog failures** injected with a **random injection intensity rate**, with a sample rate of one sample per minute, up to a system crash

* **Anomalies.zip**: the anomalous KPIs that the Deep Autoencoder detects on the datasets. The files are in the format required for the input data of both the OCSVM Classifier and the Granger Causality Analyzer.
    * **normal_w2.txt**: KPIs that the Deep Autoencoder detected as anomalous on the normal_w2 raw data
    * **normal_w3.txt**: KPIs that the Deep Autoencoder detected as anomalous on the normal_w3 raw data
    * **e1.txt**: anomalous KPIs that the Deep Autoencoder detected on the e1 raw data
    * **e2.txt**: anomalous KPIs that the Deep Autoencoder detected on the e2 raw data
    * **e3.txt**: anomalous KPIs that the Deep Autoencoder detected on the e3 raw data
    * **e4.txt**: anomalous KPIs that the Deep Autoencoder detected on the e4 raw data
    * **e5.txt**: anomalous KPIs that the Deep Autoencoder detected on the e5 raw data
    * **e6.txt**: anomalous KPIs that the Deep Autoencoder detected on the e6 raw data
    * **e7.txt**: anomalous KPIs that the Deep Autoencoder detected on the e7 raw data
    * **e8.txt**: anomalous KPIs that the Deep Autoencoder detected on the e8 raw data
    * **e9.txt**: anomalous KPIs that the Deep Autoencoder detected on the e9 raw data

> The data in these .txt files are formatted as JSON records, with each record consisting of the following fields:
> * timestamp - timestamp of the observation (date/time in Unix format)
> * resource - the node of the cluster
> * metric - metric name
> * value - value of the KPI

* **Anomalies-Premise.zip**: synthetic sequences of anomalous KPIs that we derived by replicating and grouping anomalies from the **Anomalies.zip**. We use these sequences for training and testing Premise. The file contains **anomalies-0** and **anomalies-1** folders with two different datasets we used for different experiments. Each of the two folders contains two sub-folders, **training-data** with the dataset used for training Premise and **test-data** with the dataset used for testing Premise. Each folder contains a set of directories with .txt files containing anomalous KPIs that the Deep Autoencoder detected per each observed sample (the name of the folders, **xxxxxxxxxx-xx.xx.x.xxx**, is a combination of a sequential identifier and the IP address of the machine used in the experiments, the names of the .txt files in the folders indicate the minutes passed from the start of the experiment):
    * **xxxxxxxxxx-xx.xx.x.xxx-MemL@Exp_{N}_Exp**: anomalous KPIs detected for execution with Memory Leak failures injected into the master-slave pair number N with exponential intensity pattern.
    * **xxxxxxxxxx-xx.xx.x.xxx-MemL@Lin_{N}_Lin**: anomalous KPIs detected for execution with Memory Leak failures injected into the master-slave pair number N with linear intensity pattern.
    * **xxxxxxxxxx-xx.xx.x.xxx-MemL@Rnd_{N}_Rnd**: anomalous KPIs detected for execution with Memory Leak failures injected into the master-slave pair number N with random intensity pattern.
    * **xxxxxxxxxx-xx.xx.x.xxx-PacL@Lin_{N}_Lin**: anomalous KPIs detected for execution with Packet Loss failures injected into the master-slave pair number N with linear intensity pattern.
    * **xxxxxxxxxx-xx.xx.x.xxx-PacL@Exp_{N}_Exp**: anomalous KPIs detected for execution with Packet Loss failures injected into the master-slave pair number N with exponential intensity pattern.
    * **xxxxxxxxxx-xx.xx.x.xxx-PacL@Rnd_{N}_Rnd**: anomalous KPIs detected for execution with Packet Loss failures injected into the master-slave pair number N with random intensity pattern.
    * **xxxxxxxxxx-xx.xx.x.xxx-CpuH@Exp_{N}_Exp**: anomalous KPIs detected for execution with CPU Hog failures injected into the master-slave pair number N with exponential intensity pattern.
    * **xxxxxxxxxx-xx.xx.x.xxx-CpuH@Lin_{N}_Lin**: anomalous KPIs detected for execution with CPU Hog failures injected into the master-slave pair number N with linear intensity pattern.
    * **xxxxxxxxxx-xx.xx.x.xxx-CpuH@Rnd_{N}_Rnd**: anomalous KPIs detected for execution with CPU Hog failures injected into the master-slave pair number N with random intensity pattern.
    * **xxxxxxxxxx-xx.xx.x.xxx-failurefree_x_x**: sets of normal (not anomalous) KPIs detected as anomalous for execution with normal (without fault seeding) conditions.
    
> These folders contain .txt files that report the sets of anomalous KPIs observed at each timestamp of the experiments. Each row of the .txt files refers to a KPI and consists of 3 parts separated by comma:
> * Number of the master-slave pair of the cluster
> * Constant value (symbol "x" - not used)
> * Name of the KPI 
>
> Example: ('6', 'x', 'redis-8_system.network.in.packets')
    

* **Classifications-Premise.zip**: output of **Premise** classifier. It consists of two subfolders that contain the classification results obtained with **Premise** trained with different datasets - training data from **anomalies-0** and **anomalies-1** folders of **Anomalies-Premise.zip**. Each of the two directories contains the folders corresponding to the predictions of **Premise** done on datasets collected from executions with different failure types seeded into the master-slave pair number 0 with different injection intensity patterns:
    * **xxxxxxxxxx-xx.xx.x.xxx-MemL@Exp_0_Exp**: contains a .txt file with classifications for each observation for dataset with **Memory Leak** failures injected into the master-slave pair number 0 with **exponential pattern**. Each row indicates a predicted failure type, failure injection pattern, and the master-slave pair number.
    * **xxxxxxxxxx-xx.xx.x.xxx-MemL@Lin_0_Lin**: contains a .txt file with classifications for each observation for dataset with **Memory Leak** failures injected into the master-slave pair number 0 with **linear pattern**. Each row indicates a predicted failure type, failure injection pattern, and the master-slave pair number.
    * **xxxxxxxxxx-xx.xx.x.xxx-MemL@Rnd_0_Rnd**: contains a .txt file with classifications for each observation for dataset with **Memory Leak** failures injected into the master-slave pair number 0 with **random pattern**. Each row indicates a predicted failure type, failure injection pattern, and the master-slave pair number.
    * **xxxxxxxxxx-xx.xx.x.xxx-PacL@Lin_0_Lin**: contains a .txt file with classifications for each observation for dataset with **Packet Loss** failures injected into the master-slave pair number 0 with **linear pattern**. Each row indicates a predicted failure type, failure injection pattern, and the master-slave pair number.
    * **xxxxxxxxxx-xx.xx.x.xxx-PacL@Exp_0_Exp**: contains a .txt file with classifications for each observation for dataset with **Packet Loss** failures injected into the master-slave pair number 0 with **exponential pattern**. Each row indicates a predicted failure type, failure injection pattern, and the master-slave pair number.
    * **xxxxxxxxxx-xx.xx.x.xxx-PacL@Rnd_0_Rnd**: contains a .txt file with classifications for each observation for dataset with **Packet Loss** failures injected into the master-slave pair number 0 with **random pattern**. Each row indicates a predicted failure type, failure injection pattern, and the master-slave pair number.
    * **xxxxxxxxxx-xx.xx.x.xxx-CpuH@Exp_0_Exp**: contains a .txt file with classifications for each observation for dataset with **CPU Hog** failures injected into the master-slave pair number 0 with **exponential pattern**. Each row indicates a predicted failure type, failure injection pattern, and the master-slave pair number.
    * **xxxxxxxxxx-xx.xx.x.xxx-CpuH@Lin_0_Lin**: contains a .txt file with classifications for each observation for dataset with **CPU Hog** failures injected into the master-slave pair number 0 with **linear pattern**. Each row indicates a predicted failure type, failure injection pattern, and the master-slave pair number.
    * **xxxxxxxxxx-xx.xx.x.xxx-CpuH@Rnd_0_Rnd**: contains a .txt file with classifications for each observation for dataset with **CPU Hog** failures injected into the master-slave pair number 0 with **random pattern**. Each row indicates a predicted failure type, failure injection pattern, and the master-slave pair number.

> These folders contain a LMT.txt file that reports predictions for each timestamp. Each row of the file indicates a predicted failure type and failure injection pattern at a the master-slave pair, formatted as {failure type}@{injection pattern}_{master-slave pair number}. We use the string "failurefree_none" to denote negative classifications.



* **Classifications-Prevent-A.zip**: output of **PREVENT-A Classifier** - classifications made on the datasets with normal data and data collected from the executions with seeded faults. It contains a set of files with classifications per timestamp where 0 corresponds to normal state and 1 indicates a failure:

    * **normal_w3.csv**: classifications per timestamp for dataset collected with normal execution conditions (one week of normal data).
    * **e1.csv**: classifications per timestamp for the dataset with **Memory Leak** failures injected with **exponential pattern**.
    * **e2.csv**: classifications per timestamp for the dataset with **Memory Leak** failures injected with **linear pattern**.
    * **e3.csv**: classifications per timestamp for the dataset with **Memory Leak** failures injected with **random pattern**.
    * **e4.csv**: classifications per timestamp for the dataset with **Packet Loss** failures injected with **linear pattern**.
    * **e5.csv**: classifications per timestamp for the dataset with **Packet Loss** failures injected with **exponential pattern**.
    * **e6.csv**: classifications per timestamp for the dataset with **Packet Loss** failures injected with **random pattern**.
    * **e7.csv**: classifications per timestamp for the dataset with **CPU Hog** failures injected with **exponential pattern**.
    * **e8.csv**: classifications per timestamp for the dataset with **CPU Hog** failures injected with **linear pattern**.
    * **e9.csv**: classifications per timestamp for the dataset with **CPU Hog** failures injected with **random pattern**.

> The .csv files report the predictions at each timestamp, where 0 means normal state and 1 indicates failure alert.

* **Classifications-Prevent-E.zip**: output of **PREVENT-E Classifier**- classifications made on the datasets with normal data and data collected from the executions with seeded faults. It contains a set of files with classifications per timestamp where 0 corresponds to normal state and 1 indicates a failure:

    * **normal_w3.csv**: classifications per timestamp for dataset collected with normal execution conditions (one week of normal data).
    * **e1.csv**: classifications per timestamp for the dataset with **Memory Leak** failures injected with **exponential pattern**.
    * **e2.csv**: classifications per timestamp for the dataset with **Memory Leak** failures injected with **linear pattern**.
    * **e3.csv**: classifications per timestamp for the dataset with **Memory Leak** failures injected with **random pattern**.
    * **e4.csv**: classifications per timestamp for the dataset with **Packet Loss** failures injected with **linear pattern**.
    * **e5.csv**: classifications per timestamp for the dataset with **Packet Loss** failures injected with **exponential pattern**.
    * **e6.csv**: classifications per timestamp for the dataset with **Packet Loss** failures injected with **random pattern**.
    * **e7.csv**: classifications per timestamp for the dataset with **CPU Hog** failures injected with **exponential pattern**.
    * **e8.csv**: classifications per timestamp for the dataset with **CPU Hog** failures injected with **linear pattern**.
    * **e9.csv**: classifications per timestamp for the dataset with **CPU Hog** failures injected with **random pattern**.

> The .csv files report the predictions at each timestamp, where 0 means normal state and 1 indicates failure alert.


* **Localizations-Loud.zip**: output of Loud - localizations made on the datasets with normal data and data collected from the executions with seeded faults. It contains a set of files with localizations for each observation.

    * **normal_w3.csv**: localizations per timestamp for dataset collected with one week of normal execution.
    * **e1.csv**: localizations per timestamp for the dataset with **Memory Leak** failures injected with **exponential pattern**.
    * **e2.csv**: localizations per timestamp for the dataset with **Memory Leak** failures injected with **linear pattern**.
    * **e3.csv**: localizations per timestamp for the dataset with **Memory Leak** failures injected with **random pattern**.
    * **e4.csv**: localizations per timestamp for the dataset with **Packet Loss** failures injected with **linear pattern**.
    * **e5.csv**: localizations per timestamp for the dataset with **Packet Loss** failures injected with **exponential pattern**.
    * **e6.csv**: localizations per timestamp for the dataset with **Packet Loss** failures injected with **random pattern**.
    * **e7.csv**: localizations per timestamp for the dataset with **CPU Hog** failures injected with **exponential pattern**.
    * **e8.csv**: localizations per timestamp for the dataset with **CPU Hog** failures injected with **linear pattern**.
    * **e9.csv**: localizations per timestamp for the dataset with **CPU Hog** failures injected with **random pattern**.

> The rows of the .csv files correspond to the localizations provided by the anomaly ranker at a timestamp:
> * timestamp: timestamp in "yyyy-mm-ddTh:m:s.000Z" format, where "000Z" is a constant. Example: 2020-4-13T19:13:00.000Z.
> * the node localized as faulty
> * the node that localized as the first suspicious one
> * the number of anomalous metrics of the first suspicious node
> * the node that localized as a second suspicious one
> * the number of anomalous metrics of the second suspicious node
> ... and so forth
    
* **Workload.zip**: the workload profile used to generate a load on the target application cluster. The .txt file contains comma-separated numeric values representing the intensity of a workload for every 15 minutes of execution.

<br>
<br>

##  References:
---
[1] Giovanni Denaro, Rahim Heydarov, Ali Mohebbi, Mauro Pezzè,PREVENT: An Unsupervised Approach to Predict Software Failures in Production, submitted to IEEE TSE February 2022.

[2] Leonardo Mariani, Mauro Pezzè, Oliviero Riganelli, and Rui Xin. Predicting failures in multi-tier distributed systems. Journal of Systems and Software, 161, 2020. URL: https://star.inf.usi.ch/media/papers/2020-jss-mariani-premise.pdf

[3] Leonardo Mariani, Cristina Monni, Mauro Pezzè, Oliviero Riganelli, and Rui Xin. Localizing faults in cloud systems. In Proceedings of the International Conference on Software Testing, Veriﬁcation and Validation, ICST '18, pages 262–273. IEEE Computer Society, 2018. URL: https://star.inf.usi.ch/media/papers/2018-icst-mariani-load.pdf
