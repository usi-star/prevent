import os

print("\n", "False Positive Rate of prediction for Prevent-A, Prevent-E, and Loud", "\n")

# Calculate FPR for Prevent-A
os.system('python calculate-fpr-normal-data-prevent.py prevent-a normal_w3')
# Calculate FPR for Prevent-E
os.system('python calculate-fpr-normal-data-prevent.py prevent-e normal_w3')
# Calculate FPR for Loud
os.system('python calculate-fpr-normal-data-loud.py loud normal_w3')