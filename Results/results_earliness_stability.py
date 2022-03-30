import os

# Generate the consolidated reports
os.system('python generate-reports.py')

print("\n", "Prediction earliness (minutes before the system crash) and stability (TPR) of prediction", "\n")
# Calculate Earliness and Stability of prediction for Prevent-A, Prevent-E, and Loud
os.system('python calculate-earliness-and-stability.py')