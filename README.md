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

* **KPI**: Key Performance Indicators, values of the metrics collected at the cluster nodes.
* **State Classifier**: the component of Prevent that predicts failures based on the analysis of the KPIs.
* **Anomaly Ranker**: the component of Prevent and Loud that locates the sources of the failure propagation by statistically testing the relations between the KPIs.
* **Deep Autoencoder**: the sub-component of Prevent State Classifier and a sub-component of Anomaly Ranker that detects anomalous KPIs (concerning the observations in the training phase) in the observed data.
* **Granger Causality Analyzer**: the sub-component of the Anomaly Ranker that conducts a Granger Causality analysis by building a causality graph representing the KPIs' causal dependencies.
* **OCSVM Classifier**: the sub-component of Prevent State Classifier, represented by a one-class-support-vector-machine (OCSVM) classiﬁer that discriminates between failure-prone and benign sets of anomalies.
* **master-slave pair** - a pair of master-slave nodes of the target application (Redis cluster). In our experiments, we used a cluster consisting of 10 master-slave pairs.

<br/>
<br/>

## Datasets and results
---
<br/>

### Naming Conventions
<br/>

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

<br>

###  The content of the Datasets directory
<br>

* **Datasets-Raw**: sets of KPI values obtained by monitoring the target application (Redis cluster) executed both in normal conditions, that is, with no failures, and in failing states, that is, with injected failures. The folder includes .csv files with different datasets:

    * **normal_w1.csv.zip**: KPIs collected during a week of normal execution, that is, without injected faults, with a sample rate of one sample per minute 
    * **normal_w2.csv.zip**: KPIs collected during a week of normal execution, that is, without injected faults, with a sample rate of one sample per minute
    * **normal_w1_2.csv.zip**: KPIs collected during two weeks of normal execution, that is, without injected faults, with a sample rate of one sample per minute
    * **normal_w3.csv.zip**: KPIs collected during a week of normal execution, that is, without injected faults, with a sample rate of one sample per minute
    * **e1.csv** - KPIs collected during execution with  **memory leak** failures injected with an **exponential** injection intensity rate, with a sample rate of one sample per minute, up to a system crash
    * **e2.csv** - KPIs collected during execution with  **memory leak** failures injected with a **linear** injection intensity rate, with a sample rate of one sample per minute, up to a system crash
    * **e3.csv** - KPIs collected during execution with  **memory leak** failures injected with a **random** injection intensity rate, with a sample rate of one sample per minute, up to a system crash
    * **e4.csv**  - KPIs collected during execution with  **packet loss** failures injected with a **linear** injection intensity rate, with a sample rate of one sample per minute, up to a system crash
    * **e5.csv**  - KPIs collected during execution with  **packet loss** failures injected with an **exponential** injection intensity rate, with a sample rate of one sample per minute, up to a system crash
    * **e6.csv**  - KPIs collected during execution with  **packet loss** failures injected with a **random** injection intensity rate, with a sample rate of one sample per minute, up to a system crash
    * **e7.csv**  - KPIs collected during execution with  **CPU hog** failures injected with an **exponential** injection intensity rate, with a sample rate of one sample per minute, up to a system crash
    * **e8.csv**  - KPIs collected during execution with  **CPU hog** failures injected with a **linear** injection intensity rate, with a sample rate of one sample per minute, up to a system crash
    * **e9.csv**  - KPIs collected during execution with  **CPU hog** failures injected with a **random** injection intensity rate, with a sample rate of one sample per minute, up to a system crash

>These files are provided in the form of comma separated values (.csv) files, where each row corresponds to a set of KPI values collected at a timestamp:
> * Columns A: timestamp in "yyyy-mm-ddThours:minutes:seconds.000Z" format, where "000Z" is a constant. Example: 2020-4-13T19:13:00.000Z.
>   * Columns B..ZZ: KPI == values of the metrics collected at the cluster nodes; the title row provides <node, metrics> identifiers.

* **Datasets-Raw-Splitted.zip**: sets of KPI values obtained by monitoring the target application (Redis cluster) executed both in normal conditions, that is, with no failures, and in failing states, that is, with injected failures. This folder contains the data sets from the Datasets-Raw folder split into .csv files by the samples of 30 consecutive observations and distributed by the following folders:

    * **normal_w1.zip**: KPIs collected during a week of normal execution, that is, without injected faults, with a sample rate of one sample per minute
    * **normal_w2.zip**: KPIs collected during a week of normal execution, that is, without injected faults, with a sample rate of one sample per minute
    * **normal_w1_2.zip**: KPIs collected during two weeks of normal execution, that is, without injected faults, with a sample rate of one sample per minute
    * **normal_w3.zip**: KPIs collected during a week of normal execution, that is, without injected faults, with a sample rate of one sample per minute
    * **e1** - KPIs collected during execution with  **memory leak** failures injected with an **exponential** injection intensity rate, with a sample rate of one sample per minute, up to a system crash
    * **e2** - KPIs collected during execution with  **memory leak** failures injected with a **linear** injection intensity rate, with a sample rate of one sample per minute, up to a system crash
    * **e3** - KPIs collected during execution with  **memory leak** failures injected with a **random** injection intensity rate, with a sample rate of one sample per minute, up to a system crash
    * **e4**  - KPIs collected during execution with  **packet loss** failures injected with a **linear** injection intensity rate, with a sample rate of one sample per minute, up to a system crash
    * **e5**  - KPIs collected during execution with  **packet loss** failures injected with an **exponential** injection intensity rate, with a sample rate of one sample per minute, up to a system crash
    * **e6**  - KPIs collected during execution with  **packet loss** failures injected with a **random** injection intensity rate, with a sample rate of one sample per minute, up to a system crash
    * **e7**  - KPIs collected during execution with  **CPU hog** failures injected with an **exponential** injection intensity rate, with a sample rate of one sample per minute, up to a system crash
    * **e8**  - KPIs collected during execution with  **CPU hog** failures injected with a **linear** injection intensity rate, with a sample rate of one sample per minute, up to a system crash
    * **e9**  - KPIs collected during execution with  **CPU hog** failures injected with a **random** injection intensity rate, with a sample rate of one sample per minute, up to a system crash

* **Anomalies.zip**: the anomalous KPIs that the Deep Autoencoder detects on the Datasets-Raw-Splitted datasets. The files are in the format required for the input data of both the OCSVM Classifier and the Granger Causality Analyzer.
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
    * **xxxxxxxxxx-xx.xx.x.xxx-failurefree_x_x**: sets of KPIs detected as anomalous on samples observed during execution with normal (without fault seeding) conditions.
    
> Each .txt file in the folder contains the sets of anomalous KPIs observed at a given timestamp of the experiments. The file's name is the timestamp expressed as the number of minutes from the beginning of the experiment. Each row of the .txt file refers to a KPI and consists of 3 elements separated by a comma:
> * Number of the master-slave pair where the KPI value is collected
> * Constant value (symbol "x" - not used)
> * Name of the KPI 
>
> Example: ('6', 'x', 'redis-8_system.network.in.packets')
    

* **Classifications-Premise.zip**: the output of the Premise classifier. It consists of two subfolders that contain the classification results obtained using Premise trained with different datasets - training data from anomalies-0 and anomalies-1 folders of the **Anomalies-Premise** dataset. Each of the two directories contains the folders corresponding to the predictions of Premise done on datasets collected from executions with different failure types seeded into the master-slave pair number 0 with different injection intensity patterns:

    * **xxxxxxxxxx-xx.xx.x.xxx-MemL@Exp_0_Exp**: contains a .txt file with classifications for each observation for dataset with **Memory Leak** failures injected into the master-slave pair number 0 with **exponential pattern**.
    * **xxxxxxxxxx-xx.xx.x.xxx-MemL@Lin_0_Lin**: contains a .txt file with classifications for each observation for dataset with **Memory Leak** failures injected into the master-slave pair number 0 with **linear pattern**.
    * **xxxxxxxxxx-xx.xx.x.xxx-MemL@Rnd_0_Rnd**: contains a .txt file with classifications for each observation for dataset with **Memory Leak** failures injected into the master-slave pair number 0 with **random pattern**.
    * **xxxxxxxxxx-xx.xx.x.xxx-PacL@Lin_0_Lin**: contains a .txt file with classifications for each observation for dataset with **Packet Loss** failures injected into the master-slave pair number 0 with **linear pattern**.
    * **xxxxxxxxxx-xx.xx.x.xxx-PacL@Exp_0_Exp**: contains a .txt file with classifications for each observation for dataset with **Packet Loss** failures injected into the master-slave pair number 0 with **exponential pattern**.
    * **xxxxxxxxxx-xx.xx.x.xxx-PacL@Rnd_0_Rnd**: contains a .txt file with classifications for each observation for dataset with **Packet Loss** failures injected into the master-slave pair number 0 with **random pattern**.
    * **xxxxxxxxxx-xx.xx.x.xxx-CpuH@Exp_0_Exp**: contains a .txt file with classifications for each observation for dataset with **CPU Hog** failures injected into the master-slave pair number 0 with **exponential pattern**.
    * **xxxxxxxxxx-xx.xx.x.xxx-CpuH@Lin_0_Lin**: contains a .txt file with classifications for each observation for dataset with **CPU Hog** failures injected into the master-slave pair number 0 with **linear pattern**.
    * **xxxxxxxxxx-xx.xx.x.xxx-CpuH@Rnd_0_Rnd**: contains a .txt file with classifications for each observation for dataset with **CPU Hog** failures injected into the master-slave pair number 0 with **random pattern**.

> These folders contain a LMT.txt file that reports predictions for each timestamp. Each row of the file indicates a predicted failure type and failure injection pattern at a the master-slave pair, formatted as {failure type}@{injection pattern}_{master-slave pair number}. We use the string "failurefree_none" to denote negative classifications.



* **Classifications-Prevent-A.zip**: the output of PREVENT-A Classifier - classifications made on the datasets with normal data and data collected from the executions with seeded faults. It contains a set of .csv files with classifications for each observation:

    * **normal_w3.csv**: classifications per timestamp for the dataset collected with normal execution conditions (one week of normal data).
    * **e1.csv**: classifications per timestamp for the dataset with **Memory Leak** failures injected with **exponential** rate.
    * **e2.csv**: classifications per timestamp for the dataset with **Memory Leak** failures injected with **linear** rate.
    * **e3.csv**: classifications per timestamp for the dataset with **Memory Leak** failures injected with **random** rate.
    * **e4.csv**: classifications per timestamp for the dataset with **Packet Loss** failures injected with **linear** rate.
    * **e5.csv**: classifications per timestamp for the dataset with **Packet Loss** failures injected with **exponential** rate.
    * **e6.csv**: classifications per timestamp for the dataset with **Packet Loss** failures injected with **random** rate.
    * **e7.csv**: classifications per timestamp for the dataset with **CPU Hog** failures injected with **exponential** rate.
    * **e8.csv**: classifications per timestamp for the dataset with **CPU Hog** failures injected with **linear** rate.
    * **e9.csv**: classifications per timestamp for the dataset with **CPU Hog** failures injected with **random** rate.

> The .csv files report the predictions at each timestamp, where 0 means normal state and 1 indicates failure alert.

* **Classifications-Prevent-E.zip**: the output of PREVENT-E Classifier - classifications made on the datasets with normal data and data collected from the executions with seeded faults. It contains a set of .csv files with classifications for each observation:

    * **normal_w3.csv**: classifications per timestamp for the dataset collected with normal execution conditions (one week of normal data).
    * **e1.csv**: classifications per timestamp for the dataset with **Memory Leak** failures injected with **exponential** rate.
    * **e2.csv**: classifications per timestamp for the dataset with **Memory Leak** failures injected with **linear** rate.
    * **e3.csv**: classifications per timestamp for the dataset with **Memory Leak** failures injected with **random** rate.
    * **e4.csv**: classifications per timestamp for the dataset with **Packet Loss** failures injected with **linear** rate.
    * **e5.csv**: classifications per timestamp for the dataset with **Packet Loss** failures injected with **exponential** rate.
    * **e6.csv**: classifications per timestamp for the dataset with **Packet Loss** failures injected with **random** rate.
    * **e7.csv**: classifications per timestamp for the dataset with **CPU Hog** failures injected with **exponential** rate.
    * **e8.csv**: classifications per timestamp for the dataset with **CPU Hog** failures injected with **linear** rate.
    * **e9.csv**: classifications per timestamp for the dataset with **CPU Hog** failures injected with **random** rate.

> The .csv files report the predictions at each timestamp, where 0 means normal state and 1 indicates failure alert.


* **Localizations-Loud.zip**: the output of Loud - localizations made on the datasets with normal data and data collected from the executions with seeded faults. It contains a set of .csv files with localizations for each observation:

    * **normal_w3.csv**: localizations per timestamp for the dataset collected with normal execution conditions (one week of normal data).
    * **e1.csv**: localizations per timestamp for the dataset with **Memory Leak** failures injected with **exponential** rate.
    * **e2.csv**: localizations per timestamp for the dataset with **Memory Leak** failures injected with **linear** rate.
    * **e3.csv**: localizations per timestamp for the dataset with **Memory Leak** failures injected with **random** rate.
    * **e4.csv**: localizations per timestamp for the dataset with **Packet Loss** failures injected with **linear** rate.
    * **e5.csv**: localizations per timestamp for the dataset with **Packet Loss** failures injected with **exponential** rate.
    * **e6.csv**: localizations per timestamp for the dataset with **Packet Loss** failures injected with **random** rate.
    * **e7.csv**: localizations per timestamp for the dataset with **CPU Hog** failures injected with **exponential** rate.
    * **e8.csv**: localizations per timestamp for the dataset with **CPU Hog** failures injected with **linear** rate.
    * **e9.csv**: localizations per timestamp for the dataset with **CPU Hog** failures injected with **random** rate.

> The rows of the .csv files correspond to the localization provided by the anomaly ranker at a timestamp:
> * timestamp: timestamp in "yyyy-mm-ddThours:minutes:seconds.000Z" format, where "000Z" is a constant. Example: 2020-4-13T19:13:00.000Z.
> * the node localized as faulty that in this dataset is the first node in the ranking. This cell is empty if the number of anomalous metrics of the node that occurs first in the ranking is equal to the number of anomalous metrics of the node that occurs second.
> * the first node in the ranking
> * the number of anomalous metrics of the node that occurs first in the ranking
> * the second node in the ranking
> * the number of anomalous metrics of the node that occurs second in the ranking
> *    and so forth
    
* **Workload.zip**: the workload profile used to generate a load on the target application cluster. The .txt file contains comma-separated numeric values representing the intensity of a workload for every 15 minutes of execution.

<br>
<br>


## RESULTS
### Folder: Results
### Summary

> This folder contains a set of scripts consolidating and presenting the final results of the experiments provided in the paper.

### Prerequisites:
- OS: tested on macOS Catalina
- Python version=3.7
- Pip version=22.0.4

### 1. cd Results
### 2. Initialize the environment
    
    # Activate the environment
    source venv/bin/activate

    # Install the packages
    python -m pip install -r requirements.txt

<br>

### 3. Calculate False Positive Rate of predictions for Prevent-A, Prevent-E, and Loud (Table 3 of the paper)

    python  results_fpr.py

- Input:
    - Dataset: Classifications-Prevent-A :: normal_w3
    - Dataset: Classifications-Prevent-E :: normal_w3
    - Localizations-Loud :: normal_w3
- Output: False Positive Rates for Prevent-A, Prevent-E, and Loud

<br>

### 4. Calculate Earliness and Stability of prediction for Prevent-A, Prevent-E, and Loud (Tables 4, 5, 6 of the paper)

    python results_earliness_stability.py

- Input:
    - Dataset: Classifications-Prevent-A :: e1:9
    - Dataset: Classifications-Prevent-E :: e1:9
    - Dataset: Localizations-Loud :: e1:9
    - Dataset: Classifications-Premise
- Output: Prediction earliness and stability related information for Prevent-A, Prevent-E, and Premise

<br>

### 5. Draw the Predictions graph for Prevent-A, Prevent-E, and Premise (Figures 6, 7, 8 of the paper)

    python results_graph_predictions.py

- Input:
    - Dataset: Classifications-Prevent-A :: e1:9
    - Dataset: Classifications-Prevent-E :: e1:9
    - Dataset: Localizations-Loud :: localizations-pairs :: e1:9
    - Dataset: Classifications-Premise
- Output: Predictions graph for Prevent-A, Prevent-E, and Premise

<br>

### 6. Draw the ROC curve for Prevent-A, Prevent-E, and Premise (Figure 9 of the paper)

    python results_graph_roc.py

- Input:
    - Dataset: Classifications-Prevent-A :: e1:9
    - Dataset: Classifications-Prevent-E :: e1:9
    - Dataset: Localizations-Loud :: localizations-pairs :: e1:9
    - Dataset: Classifications-Premise
- Output: ROC curve for Prevent-A, Prevent-E, and Premise


<br>
<br>



## Toolsets and the replication instructions

<br>

Unzip the following archives after cloning the repository:
- resouces/data/Datasets-Raw-Splitted:
    - normal_w1
    - normal_w2
    - normal_w3
    - normal_w1_2
- resouces/data/Datasets-Raw:
    - normal_w1
    - normal_w2
    - normal_w3
    - normal_w1_2
- resouces/data/anomalies (in case you do not regenerate the anomalies on normal data - see the "Detect anomalies" paragraph of Prevent-A)
    - normal_w2
    - normal_w3

<br>

### Toolset: Prevent-E
#### Project folder: Toolset-Prevent-E

<br>

#### Summary
> Prevent-E trains RBM (Restricted Bolzman Machine) model and exploits it to classify each data sample (set of KPIs) observed at regular time intervals in production. It exploit a Gibbs free energy which grows when increasingly large subsets of KPIs align their states to correlated anomalous values. The higher the computed energy, the higher the likelihood of some system anomaly that manifests as anomalous values of increasing sets of correlated KPIs. Prevent-E classifies samples as anomalous when the energy values observed at runtime exceed some threshold values computed by training the network with data collected during normal execution.

<br>

#### Prerequisites:

Software:

- OS: tested on macOS Catalina
- MatLab R2019b (no exertnal tool/package installed)

Hardware used:

- MacBook Pro, OS: macOS Catalina 10.15.4
- Processor : 2.7 GHz Quad-Core Intel Core i7
- RAM : 16 GB 1600 MHz DDR3

<br>

#### 1. cd Toolset-Prevent-E

#### 2. Train & Predict

    Execute the main.m script in Matlab

- Input:
    - for training:
        - Datasets-Raw-Splitted -> normal_w1_2
    - for prediction:
        - Datasets-Raw-Splitted :: e1:9
        - Datasets-Raw-Splitted :: normal_w3
- Output:
    - Classifications-Prevent-E :: e1:9
    - Classifications-Prevent-E :: normal_w3


<br><br>

### Toolset: Anomaly Ranker
#### Project folder: Toolset-AnomalyRanker

<br>

#### Summary

> Anomaly Ranker exploits anomalous KPIs, that is, KPIs with values that signiﬁcantly differ from values observed during training in normal execution conditions, for ranking anomalous nodes according to their relevance with respect to the anomalous KPIs. Anomaly Ranker returns a list of anomalous nodes ranked by anomaly relevance, list that the Anomaly ranker produces in the presence of anomalous states inferred with the State classiﬁer. The anomalous states correlate with incoming failures, and the anomalous nodes indicate the more likely nodes that will lead to failure.

<br>

#### Prerequisites:
- OS: tested on macos Catalina
- Python version 3.6
- Pip version 22.0.4
- Python virtual environment: pipenv (version 2018.11.26 used). Installation instructions - https://pypi.org/project/pipenv/

<br>

### 3. cd Toolset-AnomalyRanker
### 4. Environment initialization
    
    # Install packages
    pipenv install

    # Activate the environment
    pipenv shell

    # Start the Anomaly Ranker server
    python ranker_app.py 5000

<br><br>


### Toolset: Prevent-A
#### Project folder: Toolset-Prevent-A

<br>

#### Summary

> Prevent-A State classiﬁer predicts failures by combining a deep autoencoder with a one-class-support-vector-machine (OCSVM) classiﬁer. The deep autoencoder model identiﬁes anomalous KPIs as KPIs with values that are anomalous with respect to the observations when training with normal executions. The OCSVM classiﬁer discriminates between benign sets of anomalies (which resemble combinations of anomalies occasionally observed during training) and failureprone sets of anomalies (which signiﬁcantly differ form the observations during training).

<br>

#### Prerequisites:
- OS: tested on macos Catalina
- Python version 3.7
- Pip version 22.0.4
- Anomaly Ranker server running on port 5000

<br>

#### 5. cd Toolset-Prevent-A
#### 6. Environment initialization
    
    # Activate the environment
    source venv/bin/activate

    # Install the packages
    python -m pip install -r requirements.txt

<br>

#### 7. Detect anomalies

    python detect.py production

- Input:
    - Datasets-Raw-Splitted :: e1:9
    - Datasets-Raw-Splitted :: normal_w3

- Output:
    - Anomalies :: e1:9
    - Anomalies :: normal_w3

<br>

#### 8. Make predictions

    python predict.py

- Input:
    - Anomalies :: e1:9
    - Anomalies :: normal_w3
- Output:
    - Classifications-Prevent-A :: e1:9
    - Classifications-Prevent-A :: normal_w3

<br>

#### 9. Localize failures

    python rank.py

- Input:
    - Anomalies :: e1:9
    - Anomalies :: normal_w3
- Output: 
    - Localizations-Loud :: e1:9
    - Localizations-Loud :: normal_w3

<br><br>


### Toolset: Premise Preprocessor
#### Folder: Preprocessor-Premise

<br>

#### Summary
> This toolset is used to prepare an input data for processing by Premise.

<br>

#### Prerequisites:

- OS: tested on macos Catalina
- Python version 3.7
- Pip version 22.0.4

<br>

#### 10. cd Preprocessor-Premise
#### 11. Environment initialization
    
    # Activate the environment
    source venv/bin/activate

    # Install the packages
    python -m pip install -r requirements.txt

<br>

#### 12. Preprocess the "Anomalies :: e1:9" dataset to be used by Premise
> Shuffle the faulty node-pairs in the anomalous datasets (change the same faulty data between the node pairs). Output - one data set for each fault-type/node-pair combination.

    python premise-data-preprocess.py

- Input: Anomalies :: e1:9
- Output: Anomalies-Premise


<br><br>


### - See the section **RESULTS** of this document for the instructions on generation of the final results.


<br><br>

##  References:
---
[1] Giovanni Denaro, Rahim Heydarov, Ali Mohebbi, Mauro Pezzè,PREVENT: An Unsupervised Approach to Predict Software Failures in Production, submitted to IEEE TSE February 2022.

[2] Leonardo Mariani, Mauro Pezzè, Oliviero Riganelli, and Rui Xin. Predicting failures in multi-tier distributed systems. Journal of Systems and Software, 161, 2020. URL: https://star.inf.usi.ch/media/papers/2020-jss-mariani-premise.pdf

[3] Leonardo Mariani, Cristina Monni, Mauro Pezzè, Oliviero Riganelli, and Rui Xin. Localizing faults in cloud systems. In Proceedings of the International Conference on Software Testing, Veriﬁcation and Validation, ICST '18, pages 262–273. IEEE Computer Society, 2018. URL: https://star.inf.usi.ch/media/papers/2018-icst-mariani-load.pdf
