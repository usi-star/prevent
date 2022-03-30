import os

# Generate report for localizations on a node pairs level (based on the localizations-loud dataset). Needed for consolidated reports of Prevent-A and Prevent-E
# os.system('python create-report-localisations-by-pairs.py')

# - Input:
# 	- Localizations-Loud :: e1:9
# - Output:
# 	- Localizations-Loud :: localizations-pairs :: e1:9


# Generate the consolidated report for prevent-a
os.system('python create-report-consolidated-prevent.py 0')

# - Input:
# 	- Classifications-Prevent-A :: e1:9
# 	- Localizations-Loud :: localizations-pairs :: e1:9
# - Output:
# 	- Consolidated report for Prevent-A


# Generate the consolidated report for prevent-e
os.system('python create-report-consolidated-prevent.py 1')

# - Input:
# 	- Classifications-Prevent-E :: e1:9
# 	- Localizations-Loud :: localizations-pairs :: e1:9
# - Output:
# 	- Consolidated report for Prevent-E


# Generate the consolidated report for premise
os.system('python create-report-consolidated-premise.py')

# - Input:
# 	- Classifications-Premise
# - Output:
# 	- Consolidated report for Premise
