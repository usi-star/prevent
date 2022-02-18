## Getting Started

<br/>
This artefact includes the data used in experiments with Prevent, Premise, and Loud approaches to comparatively evaluate their performance to predict and localize failures in dynamic systems. Prevent is defined as a combination of two approaches, PREVENT-A and PREVENT-E, that offer complementary implementations of the state classifier, both integrated with the same anomaly ranker. We introduce a new large dataset that we obtained by running a large set of experiments on REDIS, a commercially compliant, distributed cloud system. The experiments compare the stability (rate of predictions within the period between the ﬁrst valid prediction and the system crash), reliability (rate of predictions within the period before the failure injection) and earliness (time interval between the ﬁrst valid prediction and the system crash) of Prevent with Premise, when we apply the two approaches for predicting failures and localizing the failing components in REDIS cluster for a set of seeded failures.
<br/>
<br/>

## Terminology

- KPI - Key Performance Indicators, sets of metric-node values observed by monitoring the target application.

- Anomaly Detector - the component that detects anomalous KPIs in the observed data.

- State Classifier - the component that makes failure predictions based on the analysis of the KPIs.

- Anomaly Ranker - the component that locates the sources of the failure propagation by statistically testing the relations between the KPIs.


### Data

- Datasets-Raw - datasets obtained by running the target application (Redis cluster) in a standard installation and with a group of injected failures. Used to train the Anomaly Detector model and to detect anomalies
- Datasets-Consolidated - consolidated datasets obtained by running the target application (all data of the experiment consolidated in a single .csv file)
- Anomalies - the list of sets of anomalous KPI's, detected by the Anomaly Detector component. Used by Prevent-A to train the State Classifier and to make state classifications. Also used by Loud for failure localization
- Anomalies-Premise-Classifier-Input - anomalies, preprocessed to be used as an input for the Premise State Classifier. Used by Premise to train the model and to make predictions.
- Classifications-Premise-Classifier-Output - state classifications done by the Premise State Classifier
- Classifications-Prevent-A-Classifier-Output - state classifications done by the Prevent-A State Classifier
- Classifications-Prevent-E-Classifier-Output - state classifications done by the Prevent-E State Classifier
- Localizations-Loud-AnomalyRanker-Output - failure localizations done by the AnomalyRanker
- Workload-Profile - workload profile used by the Traffic Generator