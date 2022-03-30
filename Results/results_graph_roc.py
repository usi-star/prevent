import os

# Generate the consolidated reports
os.system('python generate-reports.py')

# Draw the ROC curve
os.system('python draw-graph-roc.py')