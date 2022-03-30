"""
Calculates FPR of Prevent-A and Prevent-E on normal data (normal_w3).
The timestamp is considered anomalous if it is classified by Prevent Classifier (OCSVM of Prevent-A or RBM of Prevent-E) as anomalous.
This scripts gets all the classifications from a single file with predictions (0 - negative, 1 - positive) and calculates
the rate of positive classifications.

For prevent-A:
	- Input: Classifications-Prevent-A :: normal_w3
	- Output: Print FPR
 For prevent-E:
	- Input: Classifications-Prevent-E :: normal_w3
	- Output: Print FPR
"""

import csv
import sys

project_name = sys.argv[1]
exp_code = sys.argv[2]

root_folder = "../"
classifications_file_path = root_folder + "resources/data/{project_name}/predictions/{exp_code}.csv"

# Read classification from the file (1 - positive, 0 - negative)
f = open(classifications_file_path.format(project_name=project_name, exp_code=exp_code), 'r')
reader = csv.reader(f)
classifications = []
for row in reader:
	classifications.append(int(row[0]))

# Calculate FPR
FPR = round(sum(classifications) * 100 / len(classifications))

print("False Positive Rate of", project_name, "on", exp_code, "dataset:", FPR, "%")
