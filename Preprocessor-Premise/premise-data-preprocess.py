import os

# Convert anomalies from .json to .csv format
# - Input: Anomalies :: e1:9
# - Output: Anomalies :: e1:9 in .csv
os.system('python convert-anomalies-json-to-csv.py')

# Shuffle anomalies - shuffle the faulty node-pairs in the anomalous datasets
# (change the same faulty data between the node pairs). One data set for each fault-type/node-pair combination.
# - Input: Anomalies :: e1:9 in .csv
# - Output: Anomalies :: e1:9 in .csv shuffled
os.system('python change-pairs-headers.py')

# Create training and test datasets. Writes the output data to the Premise local folder (Toolset-Premise/data)
# - Input: Anomalies :: e1:9 in .csv shuffled
# - Output: Anomalies-Premise
os.system('python create-premise-data-sets.py')