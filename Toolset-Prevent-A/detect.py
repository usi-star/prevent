import os
import sys

phase = sys.argv[1]

if phase == "training":
	os.system('python ad_detect.py normal_w2')

if phase == "production":

	# - Input:
	# 	- Datasets-Raw-Splitted :: normal_w3
	# - Output:
	# 	- Anomalies :: normal_w3
	os.system('python ad_detect.py normal_w3')

	# - Input:
	# 	- Datasets-Raw-Splitted :: e1:9
	# - Output:
	# 	- Anomalies :: e1:9
	os.system('python ad_detect.py anomalous')
