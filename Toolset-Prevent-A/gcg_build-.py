import csv
import sys
import threading
import time
import networkx as nx
import numpy as np
from statsmodels.tsa.stattools import grangercausalitytests
from scipy.ndimage.interpolation import shift
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# **** Input
data_set_code = "normal_w1_2"
gcg_filename = "gc_graph_normal_w1_2"
columns_per_thread = 10

# **** Configuration

# Numpy options
np.set_printoptions(threshold=sys.maxsize)
np.set_printoptions(suppress=True)
np.set_printoptions(formatter={'float': '{: 0.5f}'.format})

# Root directory
root_folder = "../"

# Data set file path
data_set_file_path = root_folder + "resources/data/Datasets-Raw/{data_set_code}.csv"

# GC graph file path (.gml file)
gc_gml_graph_file_path = root_folder + "resources/models/{gcg_filename}.gml"

# **** Initialization
data_set_file_path = data_set_file_path.format(data_set_code=data_set_code)
gc_gml_graph_file_path = gc_gml_graph_file_path.format(gcg_filename=gcg_filename)


# **** Functions

# Return a lag value which corresponds to the minimal p-value
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


# Load the dataset
def load_data(input_data_set_file):
	print(".. loading data .....")
	with open(input_data_set_file, 'r') as f:
		reader = csv.reader(f, delimiter=',')
		header = next(reader)
		data = np.array(list(reader))

	return header, np.array(data)


# Main class
class myThread(threading.Thread):

	def __init__(self, threadID, name, start_column, end_column):
		threading.Thread.__init__(self)

		self.threadID = threadID
		self.name = name
		self.start_column = start_column
		self.end_column = end_column
		self.gc_results = []

	def run(self):

		print(self.threadID, "Started!", self.start_column, self.end_column)

		for ii in range(self.start_column, self.end_column + 1):
			# print(self.threadID, ii, jj)

			for jj in range(number_of_columns):
				if jj == ii:
					continue

				# caused time series (target)
				y = data[ii]

				# causing time series (source)
				x = data[jj]

				# p_value of the granger causality and its lag (selects the lag corresponding to the minimal p_value)
				p_value, lag = get_gc_p_value(y, x, 3)

				if p_value <= 0.05:

					## Construct the linear regression model for prediction of the y by the lagged y and x values

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


# ***************************************************************************************************

# Load Data
header, data = load_data(data_set_file_path)
data = np.delete(data, 0, 1)
data[data == 'eth0'] = 0
data = data.transpose().astype(float)

number_of_columns = len(header)

# Get titles
kpi_titles = []

# for ii in range(len(header)):
#	kpi_titles.append(header[ii])

for ii in range(1, 1721):
	kpi_titles.append("a_" + str(ii))

print(data.shape, type(data), len(kpi_titles))

# ***************************************************************************************************

# Create the graph
DG = nx.DiGraph()

# Add nodes to the graph
for ii in range(len(kpi_titles)):
	node = kpi_titles[ii].split("_")[0]
	metric = kpi_titles[ii].split("_")[1]
	DG.add_node(kpi_titles[ii], Node=node, dataSourceType="n.a.", metric=metric, resource=node)

# Create the threads
number_of_threads = round(number_of_columns // columns_per_thread)
columns_last_thread = number_of_columns % columns_per_thread
if columns_last_thread > 0:
	number_of_threads += 1

threads = []
for ii in range(number_of_threads):
	column_start = ii * columns_per_thread

	if ii == (number_of_threads - 1):
		column_finish = column_start + columns_last_thread - 1
	else:
		column_finish = column_start + columns_per_thread - 1

	threads.append(myThread("T" + str(ii), "T" + str(ii), column_start, column_finish))

# ***************************************************************************************************

# Start the threads
start_time = time.time()
for tt in threads:
	tt.start()

# Join the threads
for tt in threads:
	tt.join()

print("--- %s seconds ---" % (time.time() - start_time))

# ***************************************************************************************************

# Save the graph as .gml file
nx.write_gml(DG, gc_gml_graph_file_path)
