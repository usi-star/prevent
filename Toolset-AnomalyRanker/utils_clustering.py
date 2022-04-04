import csv
import os

from sklearn.cluster import DBSCAN
from sklearn.cluster import AffinityPropagation
from sklearn.cluster import MeanShift
from sklearn.cluster import OPTICS
from sklearn.cluster import Birch
from sklearn.cluster import KMeans

import numpy as np
from numpy import unique


def get_clustering(data, algorithm):
    l_model = None

    if algorithm == "DBSCAN":
        l_model = DBSCAN(eps=0.001, min_samples=2).fit_predict(data)

    if algorithm == "AffinityPropagation":
        l_model = AffinityPropagation(damping=0.95).fit_predict(data)

    if algorithm == "MeanShift":
        l_model = MeanShift().fit_predict(data)

    if algorithm == "OPTICS":
        l_model = OPTICS(eps=0.001, min_samples=2).fit_predict(data)

    if algorithm == "Birch":
        l_model = Birch(threshold=0.01, n_clusters=2).fit_predict(data)

    if algorithm == "KMeans":
        l_model = KMeans(n_clusters=2).fit_predict(data)

    return l_model


def get_top_cluster_elements(data, algorithm="DBSCAN", logging=True):

    if logging:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        log_file = dir_path + "/kpi_rankings/kpi_rankings.csv"
        with open(log_file, 'a') as csv_output:
            writer = csv.writer(csv_output)
            print("data:", data)
            writer.writerows([data])

    classifications = get_clustering(np.array([[point] for point in data]), algorithm)
    needed_cluster_classification = classifications[0]

    needed_cluster_elements = []
    for ii in range(len(classifications)):
        if classifications[ii] != needed_cluster_classification:
            break
        needed_cluster_elements.append(data[ii])

    return needed_cluster_elements
