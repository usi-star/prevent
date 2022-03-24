# -*- coding: utf-8 -*-
"""The module that reads the causality graph.
"""
import networkx
import util.kpi_info as kpi_info
import util.localizer_log as localizer_log
import util.localizer_config as localizer_config

__weighted_matrix = []
__in_degree = []
__out_degree = []


def read(gml_string):
    """Reads the causality graph from a standard gml file.

    If it has previously read other gml file, it will reset the past data.

    Args:
        gml_string(str): The string in gml format. The networkx Python package
            will parse the string.

    Returns:
        True if the input is successfully parsed. Otherwise False.
    """
    global __weighted_matrix, __in_degree, __out_degree

    matrix_cache = localizer_config.load_cache('graph', 'matrix')
    in_cache = localizer_config.load_cache('graph', 'in_degree')
    out_cache = localizer_config.load_cache('graph', 'out_degree')
    if matrix_cache and in_cache and out_cache:
        __weighted_matrix = matrix_cache
        __in_degree = in_cache
        __out_degree = out_cache
        return True

    size = len(kpi_info.kpi_list)
    __weighted_matrix = [[0 for i in range(size)] for j in range(size)]
    __in_degree = [0 for i in range(size)]
    __out_degree = [0 for i in range(size)]

    try:
        g = networkx.parse_gml(gml_string.split('\n'))
    except networkx.exception.NetworkXError as e:
        localizer_log.warning("Cannot read gml file, error message:\n" + str(e))
        return False

    for source, targets in g.adj.items():
        # print("\n source / targets", source, targets)

        # --------------------------- My change

        # Original code
        # s = tuple([str(t) for t in source.split()])

        # My code
        s = tuple([source.split("_")[0], "default", source.split("_")[1]])

        # My debug
        # print("\n target kpi:", s)
        # print("\n kpi_list:\n")
        # for kpi_object in kpi_info.kpi_list:
        #     print(kpi_object)

        # --------------------------- My change end

        for target in targets:

            # print("target", target)

            weight = g.adj[source][target]['weight']

            # --------------------------- My change

            # Original code
            # t = tuple([str(t) for t in target.split()])

            # My code
            t = tuple([target.split("_")[0], "default", target.split("_")[1]])

            # My debug
            # print("\n target kpi:", t)
            # print("\n kpi_list:\n")
            # for kpi_object in kpi_info.kpi_list:
            #     print(kpi_object)

            # --------------------------- My change end

            s_idx = kpi_info.get_index(s)
            t_idx = kpi_info.get_index(t)

            # print("s_idx, t_idx, weight:", s_idx, t_idx, weight)

            if s_idx is not -1 and t_idx is not -1:
                __weighted_matrix[s_idx][t_idx] = weight
                __in_degree[t_idx] += 1
                __out_degree[s_idx] += 1

    localizer_config.save_cache(__weighted_matrix, 'graph', 'matrix')
    localizer_config.save_cache(__in_degree, 'graph', 'in_degree')
    localizer_config.save_cache(__out_degree, 'graph', 'out_degree')

    return True


def get_weighted_matrix():
    """Return the adjacency matrix of the graph.

    The feature is currently kept as a function in case of future filters

    Args:
        None

    Returns:
        The adjacency matrix, as a list.
    """
    global __weighted_matrix
    return __weighted_matrix


def get_in_degree(idx):
    """Return the incoming degreee of a KPI in the graph.

    Args:
        idx(int): the index of the KPI.

    Returns:
        The degree if the index is in the graph, otherwise 0.
    """
    global __in_degree
    if idx in __in_degree:
        return __in_degree[idx]
    else:
        return 0


def get_out_degree(idx):
    """Return the outgoing degreee of a KPI in the graph.

    Args:
        idx(int): the index of the KPI.

    Returns:
        The degree if the index is in the graph, otherwise 0.
    """
    global __out_degree
    if idx in __out_degree:
        return __out_degree[idx]
    else:
        return 0
