import csv
import os
import sys
import threading
import time
import networkx as nx
import numpy as np
from statsmodels.tsa.stattools import grangercausalitytests
from scipy.ndimage.interpolation import shift
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


# ******************************************************************************************* Functions

# returns a lag value which corresponds to the minimal p-value
def get_gc_p_value(data_caused, data_causing, max_lag):
	data_combined = np.array([data_caused, data_causing]).transpose()

	gc_res = grangercausalitytests(data_combined, maxlag=max_lag, verbose=False)

	p_value_min = 1.0
	lag_of_p_value_min = 0

	for lag in range(1, max_lag + 1):

		ssr_F_Test_p_value = round(gc_res[lag][0].get("ssr_ftest")[1], 2)

		if ssr_F_Test_p_value < p_value_min:
			p_value_min = ssr_F_Test_p_value
			lag_of_p_value_min = lag

		if p_value_min <= 0.05:
			break

	return float(p_value_min), int(lag_of_p_value_min)


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
output_gcg_filename = sys.argv[2]

data_set_file_path = os.path.join(script_dir, "resources/" + data_set_code + ".csv")
gc_gml_graph_file_path = "resources/" + output_gcg_filename + ".gml"

# ******************************************************************************************* RUN


class myThread(threading.Thread):

	def __init__(self, threadID, name, column):
		threading.Thread.__init__(self)

		self.threadID = threadID
		self.name = name
		self.column = column
		self.gc_results = []

	def run(self):

		print(self.threadID, "Started!")

		start_column = self.column * 40

		for ii in range(start_column, start_column + 40):

			if ii % 4 == 0:
				print(self.threadID, ii)

			for jj in range(number_of_columns):

				if jj == ii:
					continue

				if ii in zero_variance_cols:
					continue

				if jj in zero_variance_cols:
					continue

				# caused time series (target)
				y = data[ii]

				# causing time series (source)
				x = data[jj]

				# p_value of the granger causality and its lag (selects the lag corresponding to the minimal p_value)
				p_value, lag = get_gc_p_value(y, x, 3)

				if p_value <= 0.05:

					# Construct the linear regression model for prediction of the y by the lagged y and x values

					# lagged y values
					y_shifted = shift(y, lag)
					# lagged x values
					x_shifted = shift(x, lag)

					# Restricted model (lagged values of the y only)
					x_r = y_shifted.reshape(-1, 1)
					model = LinearRegression().fit(x_r, y)
					y_predicted = model.predict(x_r)
					mse_r = mean_squared_error(y, y_predicted)

					# Unrestricted model (lagged values of the y + lagged values of the x)
					x_unr = np.array([y_shifted, x_shifted]).transpose()
					model = LinearRegression().fit(x_unr, y)
					y_predicted = model.predict(x_unr)
					mse_unr = mean_squared_error(y, y_predicted)

					# R squared of the Unrestricted model (i.e. the causality strength of x to y)
					causality_strength = round((mse_r - mse_unr) / mse_r, 5)
					if causality_strength == 0:
						continue

					# set the names of the source / target KPIs
					source = kpi_titles[jj]
					target = kpi_titles[ii]

					# Swap target and source.
					tmp = source
					source = target
					target = tmp

					# add the source -> target edge to the graph
					DG.add_edge(source, target, weight=causality_strength)


# Load Data
header, timestamps, data = load_data(data_set_file_path)
data = data.transpose().astype(float)
number_of_columns = len(header) - 1

# Get titles
kpi_titles = []
for ii in range(1, len(header)):
	kpi_titles.append(header[ii])

# Get zero variance columns
zero_variance_cols = []
for i in range(number_of_columns):
	if np.std(data[i]) == 0:
		zero_variance_cols.append(i)

print("zero_variance_cols:", len(zero_variance_cols))

# DG: create
DG = nx.DiGraph()

# DG: add nodes
for ii in range(len(kpi_titles)):
	node = kpi_titles[ii].split("_")[0]
	metric = kpi_titles[ii].split("_")[1]
	DG.add_node(kpi_titles[ii], Node=node, dataSourceType="n.a.", metric=metric, resource=node)

start_time = time.time()
threads = []

number_of_threads = int(number_of_columns / 40)

for i in range(number_of_threads):
	threads.append(myThread("T" + str(i), "T" + str(i), i))

for t in threads:
	t.start()

for t in threads:
	t.join()

print("--- %s seconds ---" % (time.time() - start_time))

# DG: save
nx.write_gml(DG, gc_gml_graph_file_path)
