# set -x gml_directory_path GML_DIRECTORY_PATH
# set -x output_file_path OUTPUT_FILE_PATH
set timeout 1800

for file in $gml_directory_path/**.gml
    python ranker_cli.py $file --timeout $timeout --output $output_file_path
end
