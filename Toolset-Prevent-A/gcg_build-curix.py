import csv
import os
import sys
import threading
import time

import numpy as np
from PyIF import te_compute as te
from statsmodels.tsa.stattools import grangercausalitytests


def get_gc_results(data_caused, data_causing, max_lag, p_thr):
	data_combined = np.array([data_caused, data_causing]).transpose()
	gc_res = grangercausalitytests(data_combined, maxlag=max_lag, verbose=False)

	ssr_F_Test_f_value_max = 0
	ssr_F_Test_p_value_def = 1

	for lag in range(1, max_lag + 1):
		ssr_F_Test_f_value = round(gc_res[lag][0].get("ssr_ftest")[0], 2)
		ssr_F_Test_p_value = round(gc_res[lag][0].get("ssr_ftest")[1], 2)

		if ssr_F_Test_p_value <= p_thr:
			if ssr_F_Test_f_value > ssr_F_Test_f_value_max:
				ssr_F_Test_f_value_max = ssr_F_Test_f_value
				ssr_F_Test_p_value_def = ssr_F_Test_p_value

	return int(ssr_F_Test_f_value_max)


def load_data(input_data_set_file):
	with open(input_data_set_file, 'r') as f:
		reader = csv.reader(f, delimiter=',')
		header = next(reader)
		data = np.array(list(reader))

		timestamps = data[:, 0]
		data = np.delete(data, 0, 1)

	return header, timestamps, np.array(data)


# ******************************************************************************************* Configuration

script_dir = os.path.dirname(os.path.abspath(__file__))

np.set_printoptions(threshold=sys.maxsize)
np.set_printoptions(suppress=True)
np.set_printoptions(formatter={'float': '{: 0.5f}'.format})

# ******************************************************************************************* Inputs

data_set_code = sys.argv[1]

data_set_file = os.path.join(script_dir, "resources/data_sets_combined/" + data_set_code + "_comb.csv")


# ******************************************************************************************* RUN

class myThread(threading.Thread):

	def __init__(self, threadID, name, column):
		threading.Thread.__init__(self)

		self.threadID = threadID
		self.name = name
		self.column = column
		self.gc_results = []

	def run(self):

		print(self.threadID, "started")

		start_column = self.column * 20

		for ii in range(start_column, start_column + 20):
			for jj in range(number_of_columns):

				if jj == ii:
					continue

				if ii in zero_variance_cols:
					continue

				if jj in zero_variance_cols:
					continue

				results.append([ii, jj, get_gc_results(data[ii], data[jj], 1, 0.05)])


# Load Data
header, timestamps, data = load_data(data_set_file)
data = data.transpose().astype(float)
number_of_columns = len(header) - 1

# get zero variance columns
zero_variance_cols = []
for i in range(number_of_columns):
	if np.std(data[i]) == 0:
		zero_variance_cols.append(i)


start_time = time.time()

results = []

threads = []
number_of_threads = int(number_of_columns / 20)
for i in range(number_of_threads):
	threads.append(myThread("T" + str(i), "T" + str(i), i))

for t in threads:
	t.start()

for t in threads:
	t.join()

stats_best_file_path = "g_graph.txt"
with open(stats_best_file_path, 'a') as the_file:
	for res in results:
		the_file.write(str(res[0]) + ", " + str(res[1]) + ", " + str(res[2]) + '\n')

print("--- %s seconds ---" % (time.time() - start_time))