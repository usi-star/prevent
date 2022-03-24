# -*- coding: utf-8 -*-
"""The KPI file reader that parse kpi information txt file.
"""
import util.localizer_log as localizer_log
import json


def read(kpi_json):
    """Parse the KPI data from the KPI json in the SCAPI KPI file foramt.

    Args:
        kpi_json(str):the KPI json in the SCAPI KPI file foramt.

    Returns:
        A list where the indices corresponds to the KPIs indices. If the KPI is
        presented in the file, the element will be a (resource, group,
        metric_name) tuple, otherwise it will be None.
    """
    try:
        result = [(term['resource']['name'], 'default', term['metric']['name']) for term in kpi_json]
    except (KeyError, TypeError):
        result = None
    return result
