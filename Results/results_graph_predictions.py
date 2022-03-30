import os

# Generate the consolidated reports
os.system('python generate-reports.py')

# Draw the consolidated graph
os.system('python draw-graph-predictions.py')