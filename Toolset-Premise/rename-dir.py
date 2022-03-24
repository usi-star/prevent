from glob import glob
import os

search_folder_name = "/Users/usi/PycharmProjects/premise/data/anomalies"

for root, dirs, files in os.walk(search_folder_name):
    path = root.split(os.sep)
    print(os.path.basename(root))

    #file_new = file.replace(".csv", "")
    #os.rename(file, file_new)
