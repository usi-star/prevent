import csv


# **** Input
faulty_master = "redis-14"
faulty_slave = "redis-3"
experiment_data_set_codes = ["e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9"]
cluster_node_pairs_string = 'redis-14 redis-3, redis-12 redis-1, redis-5 redis-16, redis-18 redis-7, redis-4 redis-15, redis-9 redis-20, redis-8 redis-19, redis-6 redis-17, redis-10 redis-11, redis-2 redis-13'


# **** Functions
def get_pair_id(resource, pairs):
    pair_ID = None
    for ii in range(len(pairs)):
        if resource in pairs[ii]:
            pair_ID = ii

    return pair_ID


# **** Parameters
root_folder = "../"

# Input: Localisations - output of the Anomaly Ranker
localisations_by_nodes = root_folder + "resources/data/loud/localisations-nodes/{exp_code}.csv"

# Output: Localisations by the node pairs - needed for the generation of the consolidated reports (which is in its turn is used for drawing the consolidated graph)
localisations_by_pairs = root_folder + "resources/data/loud/localisations-pairs/{exp_code}.csv"


# **** RUN

cluster_node_pairs = cluster_node_pairs_string.split(", ")
for ii in range(len(cluster_node_pairs)):
    cluster_node_pairs[ii] = cluster_node_pairs[ii].split(" ")

# Loop over the data sets
for experiment_data_set_code in experiment_data_set_codes:
    with open(localisations_by_pairs.format(exp_code=experiment_data_set_code), "w") as file_out:
        localisations_stats_writer = csv.writer(file_out)
        localisations_stats_writer.writerow(["timestamp", "master_and_slave", "master_xor_slave", "neither", "1st Res Pair", "2nd Res Pair", "3rd Res Pair"])

        with open(localisations_by_nodes.format(exp_code=experiment_data_set_code), "r") as file_in:
            csv_reader = csv.reader(file_in, delimiter=',')

            # loop over the timestamps
            for row in csv_reader:
                top_3 = []

                if len(row) > 2:
                    top_3 = [row[2]]

                    if len(row) > 4:
                        top_3 = [row[2], row[4]]

                        if len(row) > 6:
                            top_3 = [row[2], row[4], row[6]]

                master_in_top_3 = faulty_master in top_3
                slave_in_top_3 = faulty_slave in top_3

                neither_in_top_3 = 0
                master_xor_slave_in_top_3 = 0
                master_and_slave_in_top_3 = 0

                if not (master_in_top_3 or slave_in_top_3):
                    neither_in_top_3 = 1

                if master_in_top_3 != slave_in_top_3:
                    master_xor_slave_in_top_3 = 1

                if master_in_top_3 and slave_in_top_3:
                    master_and_slave_in_top_3 = 1

                timestamp = row[0]

                top_3_resources = []
                for gg in range(len(top_3)):
                    pair_id = get_pair_id(top_3[gg], cluster_node_pairs)
                    top_3_resources.append(pair_id)

                localisations_stats_writer.writerow([timestamp] + [master_and_slave_in_top_3, master_xor_slave_in_top_3, neither_in_top_3] + top_3_resources)
