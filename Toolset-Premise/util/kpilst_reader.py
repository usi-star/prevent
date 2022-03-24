# -*- coding: utf-8 -*-
"""The KPI file reader that parse kpi information txt file.
"""
import util.localizer_log as localizer_log


def read(kpi_strings):
    """Parse the KPI data from the KPI string in the SCAPI KPI file foramt.

    Args:
        kpi_strings(str):the KPI string in the SCAPI KPI file foramt.

    Returns:
        A list where the indices corresponds to the KPIs indices. If the KPI is
        presented in the file, the element will be a (resource, group,
        metric_name) tuple, otherwise it will be None.
    """
    lines = kpi_strings.split('\n')
    record = {}

    cnt = 0
    while cnt < len(lines):
        l = lines[cnt]
        try:
            if l.startswith('Target KPI'):
                index = int(l.strip().split()[-1].strip('()'))
                cnt += 1
                l = lines[cnt]
                # Read '(resource, group, metric_name)'
                terms = l.strip().split()[:3]
                record[index] = terms
        except (IndexError, ValueError, AttributeError) as e:
            localizer_log.warning("kpi list parsing error:\n"
                                  + str(e))
            return None
        cnt += 1

    if not list(record.keys()):
        return []
    length = max(record.keys()) + 1
    result = []
    for i in range(length):
        if i in record:
            result.append(record[i])
        else:
            result.append(None)
    return result
