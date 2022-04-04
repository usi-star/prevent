import requests

# **** Input
server_port = 5000
# gcg_file_name = "gc_graph_n8"
gcg_file_name = "gc_graph_with_original_metric_names"

# **** Parameters

# Root directory
root_folder = "../"

# GC graph file path (.gml file)
gcg_file_path = root_folder + "resources/models/{gcg_file_name}.gml"

# Anomaly Ranker server address
server_address = "http://localhost:{server_port}"

# **** Initialization

# Source GCG file path
gcg_file_path = gcg_file_path.format(gcg_file_name=gcg_file_name)
# Anomaly Ranker server address
server_address = server_address.format(server_port=server_port)

# DG: load the graph from the .gml file
f = open(gcg_file_path.format(gcg_file_name=gcg_file_name), "r")
gcg_file_content = f.read()

# Ranker: Update GML
r = requests.post(server_address + "/update_gml", json={'gml': gcg_file_content}, headers={"Content-Type": "application/json"})
print("Ranker: Update GML: ", str(r.content))