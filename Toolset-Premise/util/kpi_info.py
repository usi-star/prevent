# -*- coding: utf-8 -*-
"""The module that stores the KPI informations.

Attributes:
    kpi_list(list): The list that stores the KPI objects, with the index also
    its GCD number.
"""
import util.kpilst_reader as kpilst_reader
import util.localizer_config as localizer_config


class KPI(object):
    """This class stores the information of single KPI.

    A KPI is composed of index, resource name, group name, metric name. The
    comparison of two KPIs is based on their resource name, group name, and
    metric name.

    Args:
        idx(int): Index of the KPI in the KPI list, usually corresponding to
            its GCD number.
        rsc(string): Resource name that the KPI belongs to.
        grp(string): Group name that the KPI's metric belongs to.
        mtr(string): Metric name of the KPI's metric.

    Attributes:
        idx(int): Index of the KPI in the KPI list, usually corresponding to
            its GCD number.
        resource(string): Resource name that the KPI belongs to.
        group(string): Group name that the KPI's metric belongs to.
        metric(string): Metric name of the KPI's metric.
        tag(string): A string reprenstation of the tuple (resource, group,
            metric)
    """
    def __init__(self, idx, rsc, grp, mtr):
        self.idx = idx
        self.resource = rsc
        self.group = grp
        self.metric = mtr
        self.tag = str((self.resource, self.group, self.metric))

    def desc(self):
        """Get a description of the KPI used for logging.

        Args:
            None

        Returns:
            The string description.
        """
        kpi_name = 'id:{idx}, resource: {rsc}, group: {grp}, metric: {mtr}'\
            .format(idx=self.idx,
                    rsc=self.resource,
                    grp=self.group,
                    mtr=self.metric)
        return kpi_name

    def __str__(self):
        return self.tag

    def __eq__(self, other):
        return self.tag == other

    def __hash__(self):
        return hash(self.tag)


# initialize KPI list
kpi_list = []
__rsc_cnt = {}


# Rahim added this function
def init(kpi_indices_file):
    global kpi_list

    file1 = open(kpi_indices_file, 'r')
    kpis = file1.readlines()

    kpi_list = []
    for kpi in kpis:

        kpi_id = kpi.split(", ")[0].split(":")[1]
        kpi_res = kpi.split(", ")[1].split(": ")[1]
        kpi_group = kpi.split(", ")[2].split(": ")[1]
        kpi_metric = kpi.split(", ")[3].split(": ")[1].strip("\n")

        kpi_obj = KPI(kpi_id, kpi_res, kpi_group, kpi_metric)
        kpi_list.append(kpi_obj)



def initialize(kpi_strings):
    """Initialize the list from a string.

    The input data should be in the form of a SCAPI KPI list file.

    Args:
        The string that contains the KPI file's content.

    Returns:
        True if it is successfully initialized, otherwise False.
    """
    global kpi_list
    global __rsc_cnt
    kpi_cache = localizer_config.load_cache('kpi', 'kpi')
    rsc_cache = localizer_config.load_cache('kpi', 'rsc')
    if kpi_cache and rsc_cache:
        kpi_list = kpi_cache
        __rsc_cnt = rsc_cache
        return True

    kpis = kpilst_reader.read(kpi_strings)
    if kpis is None:
        return False
    else:
        kpi_list = []
        __rsc_cnt = {}
        for i, kpi in enumerate(kpis):
            kpi_obj = KPI(i, *kpi) if kpi else None
            kpi_list.append(kpi_obj)
            rsc = kpi_obj.resource
            if rsc not in __rsc_cnt:
                __rsc_cnt[rsc] = 0
            __rsc_cnt[rsc] += 1

        localizer_config.save_cache(kpi_list, 'kpi', 'kpi')
        localizer_config.save_cache(__rsc_cnt, 'kpi', 'rsc')

        return True


def get_index(tag):
    """Returns the index of a KPI.

    Args:
        tag(tuple): The tag of a KPI object.

    Returns:
        The index of the KPI if found, otherwise -1.
    """
    global kpi_list
    try:
        return kpi_list.index(str(tag))
    except ValueError:
        return -1


def get_kpi_by_id(gcd):
    """Returns the KPI object by the index.

    Args:
        gcd(int): The index of a KPI.

    Returns:
        The KPI object of the index is within range, otherwise None.
    """
    global kpi_list
    idx = int(gcd)
    if idx >= 0 and gcd < len(kpi_list):
        return kpi_list[idx]
    else:
        return None


def get_kpi_by_tag(tag):
    """Returns the KPI object by the tag.

    Args:
        tag(tuple): The tag of a KPI object.

    Returns:
        The KPI object of tag can be found, otherwise None.
    """
    global kpi_list
    idx = get_index(tag)
    if idx != -1:
        return kpi_list[idx]
    else:
        return None


def write_kpi_indices(dst_file):
    """Log the indices to a file

    Args:
        dst_file(str): The file to write the indices.

    Returns:
        None
    """
    global kpi_list
    with open(dst_file, 'w') as f:
        for kpi in kpi_list:
            f.write(kpi.desc() + '\n')


def get_rsc_cnt(rsc):
    """Get the count of a resource in the KPI list.

    Args:
        rsc(str): The name of the resource.

    Returns:
        The number that indicates the count of the resource.
    """
    global __rsc_cnt
    if rsc in __rsc_cnt:
        return __rsc_cnt[rsc]
    else:
        return 0
