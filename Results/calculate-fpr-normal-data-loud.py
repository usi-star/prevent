"""
Calculates FPR of LOUD on normal data (normal_w3).
The timestamp is considered anomalous when the same pair of nodes (any pair, not necessarily master/slave pair)
persists in the top three nodes that LOUD ranks as anomalous for N consecutive timestamps.

- Input: Localizations-Loud :: localizations-nodes :: normal_w3
- Output: Print FPR

"""

import csv
import sys


# **** Input

project_name = sys.argv[1]
exp_code = sys.argv[2]

min_period = 3
max_period = 7


# **** PARAMETERS

root_folder = "../"
localisations_raw_file_path = root_folder + "resources/data/{project_name}/localisations-nodes/{exp_code}.csv"


# **** Functions
def get_prediction(raw_loc_matrix, time_point, period):

    lst = [raw_loc_matrix[time_point - ii] for ii in range(period)]
    intersection = lst[0].intersection(*lst)

    if len(intersection) >= 2:
        return 1
    else:
        return 0


# ******************************************************************************************* RUN

# Read the raw localisations matrix - vectors like [0, 1, 0] where [None, Weak, Strong] localisations.
localisations_file_reader = csv.reader(open(localisations_raw_file_path.format(project_name=project_name, exp_code=exp_code), 'r'))
raw_localisations_matrix = []
for row in localisations_file_reader:

    if len(row) >= 3:
        el1 = row[2]
    else:
        el1 = ""

    if len(row) >= 5:
        el2 = row[4]
    else:
        el2 = ""

    if len(row) >= 7:
        el3 = row[6]
    else:
        el3 = ""

    raw_localisations_matrix.append({el1, el2, el3})

print("False Positive Rate of", project_name, "on", exp_code,
      "data set for N consecutive timestamps when the same pair of nodes persists in the top three suspicious nodes:")

for period in range(min_period, max_period):

    classifications = []
    for time_point in range(len(raw_localisations_matrix)):
        classifications.append(get_prediction(raw_localisations_matrix, time_point, period=period))

    # Calculate FPR
    FPR = round(sum(classifications) * 100 / len(classifications))

    print("For N =", period, ":", FPR, "%")
