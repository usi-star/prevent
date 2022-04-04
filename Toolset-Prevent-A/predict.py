import os

# Set fake names for KPIs (a1 - a1720) in Amnomaly Ranker
os.system('python kpi_list_update.py')

# - Input:
# 	- Anomalies :: e1:9
# - Output:
# 	- Classifications-Prevent-A :: e1:9
os.system('python fp_predict_anom.py')

# - Input:
# 	- Anomalies :: normal_w3
# - Output:
# 	- Classifications-Prevent-A :: normal_w3
os.system('python fp_predict_norm.py')




