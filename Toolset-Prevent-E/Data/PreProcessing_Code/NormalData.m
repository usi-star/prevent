% Converting Gaetano's dataset to data format expected from RBM's Library
function [NormalSet, totKPI] = NormalData(nKPI, method, directory, finalDataDir, eliminateStringColumn, debug)

% Temporary directory in which store results like read dataset non processed
% and min-max values, mean, standard deviation, ecc.
tempDir = "./Data/PreProcessing_code/tmp/";
if (exist(tempDir, 'dir') ~= 7)
    mkdir(tempDir);
end

% Look for different file name depending on flag eliminateStringColumn's
% value setted in the Main.m, because the total number of KPI could vary
if eliminateStringColumn
    Files = dir(fullfile(directory,'*.csv'));
    finalTrain = readtable(fullfile(directory, Files(1).name),'PreserveVariableNames',true);
    S = vartype('numeric');
    finalTrain = [finalTrain(:, 1), finalTrain(:,S)];
    entries = size(finalTrain);
    unifiedfile = "Normal_" + entries(2) + "_Unified_Ordered" + "_NOstrings.csv";
else
    unifiedfile = "Normal_" + nKPI + "_Unified_Ordered.csv";
end


if ~exist(tempDir + unifiedfile, "file")
    % Directory in which find the .csv files
    % (Unification process of multiple .csv)
    Files = dir(fullfile(directory,'*.csv'));

    % Read the first .csv in the folder and save
    % its properties (dimensions, var names, ecc.)
    finalTrain = readtable(fullfile(directory, Files(1).name),'PreserveVariableNames',true);
    entries = size(finalTrain);
    KPIs = finalTrain.Properties.VariableNames;
    finalTrain = finalTrain(1:entries(1), 1:entries(2));

    % Read any other .csv in the folder
    for k = 2:length(Files)
        baseFileName = Files(k).name;
        fullFileName = fullfile(directory, baseFileName);
        dataset = readtable(fullFileName,'PreserveVariableNames',true);       
        dataset.Properties.VariableNames = KPIs;
        entries = size(dataset);
        Traindata = dataset(1:entries(1), 1:entries(2));
        finalTrain = [finalTrain; Traindata];
    end
    
    if eliminateStringColumn
        S = vartype('numeric');
        finalTrain = [finalTrain(:, 1), finalTrain(:,S)];        
    end
    
    entries = size(finalTrain);
    
    % Order the final dataset according to the timestamp
    sortrows(finalTrain, 'timestamp');
    
    % removing timestamps since they were useful just for guaranteeing a correct sorting
    % of the entries
    finalTrain = finalTrain(:, 2:entries(2));
    
    % The following code will convert any string column in a consistent
    % incremental numerical value, in order to be processed by the RBM
    if ~eliminateStringColumn
        entries = size(finalTrain);
        newCols = [];
        colNames = [];
        indexCols = [];
        for i = 1:entries(2)
            % If a column contining string values is found, its index, name and
            % values are stored
            if iscellstr(finalTrain(1, i).(1))
                indexCols = [ indexCols i ];
                newCols = [ newCols table2array(finalTrain(:, i)) ];
                colNames = [ colNames finalTrain.Properties.VariableNames(i) ];
            end
        end

        % Unique and consistent number from string
        shape = size(newCols);
        [~, ~, newCols] = unique(newCols, 'stable');
        newCols = reshape(newCols,shape(1),shape(2));

        % Applying the changes to the string column, by adding the new columns
        % and removing the old ones
        for i = 1:length(colNames)
            colName = colNames(i);
            finalTrain = addvars(finalTrain,newCols(:, i), 'After', colName, 'NewVariableNames', "NewTMPColumn");
            finalTrain(:, indexCols(i)) = [];
            finalTrain.Properties.VariableNames(indexCols(i)) = colName;
        end
    end

    % Covert the result table in a matrix
    Traindata = table2array(finalTrain);

    % Save the new .csv file
    csvwrite(tempDir + unifiedfile, Traindata);
    
else
    Traindata = readtable(tempDir + unifiedfile,'PreserveVariableNames',true);
    Traindata = table2array(Traindata);
end

    entries = size(Traindata);

    totKPI = entries(2);
    if debug
        disp("Unification Process finished - Normal Data");
    end

    % Unification Process termined

    %% Data preprocessing Phase
    
    if debug
       disp("Data Preprocessing Phase - Normal Data");
    end

    switch method
        case 'Stand'
            mu = zeros(entries(2), 0);
            sig = zeros(entries(2), 0);
            for i = 1:entries(2)
                mu(i) = mean(Traindata(:, i), 'all');
                sig(i) = std(Traindata(:, i), 0, 'all');
            end

            for i = 1:entries(2)
                entry = Traindata(:, i);
                current_mu = mu(i);
                current_sig = sig(i);
                for j = 1:entries(1)
                    entry(j) = (entry(j) - current_mu) / current_sig;
                    if isnan(entry(j))
                        entry(j) = 0;
                    end
                    if isinf(entry(j))
                        entry(j) = 1;
                    end
                end
                Traindata(:, i) = entry;
            end

        case 'NormMatrix'
            maxEntry = max(Traindata, [], 'all');
            minEntry = min(Traindata, [], 'all');
            for i = 1:entries(1)
                current_row = Traindata(i, :);
                for j = 1:entries(2)
                    current_row(j) = (current_row(j) - minEntry) / (maxEntry - minEntry);
                end
                Traindata(i, :) = current_row;
            end

        case 'NormKPI'
            KPIs = entries(2);
            maxKPI = zeros(KPIs, 0);
            minKPI = zeros(KPIs, 0);
            % Find the max and min entries for each column (KPI)
            for i = 1:KPIs
                maxKPI(i) = max(Traindata(:, i), [], 'all');
                minKPI(i) = min(Traindata(:, i), [], 'all');
            end
            % Apply the data Scaling
            for i = 1:KPIs
                current_row = Traindata(:, i);
                current_max = maxKPI(i);
                current_min = minKPI(i);
                for j = 1:entries(1)
                    current_row(j) = (current_row(j) - current_min) / (current_max - current_min);
                    if isnan(current_row(j))
                        current_row(j) = 0;
                    end
                    if isinf(current_row(j))
                        current_row(j) = 1;
                    end
                end
                Traindata(:, i) = current_row;
            end
            
        case 'Raw'
            % Maintain the data as it is
            
    end

    %% Saving Phase
    if debug
        disp("Saving Phase - Normal Data");
    end
    
    % Save the new .csv file
    directory = finalDataDir + "Csv/";
    if (exist(directory, 'dir') ~= 7)
        mkdir(directory);
    end    
    csvname = "Normal_" + totKPI + "_" + method + ".csv";
    out = directory + csvname;
    if ~exist(out, 'file')
        csvwrite(out, Traindata);
    end
    NormalSet = out;

    % Save the min and max KPI for test data normalization
    tmpdir = tempDir + totKPI + "_";
    
    if exist('minKPI', 'var')
        save(tmpdir + "MinMaxKPI.mat", 'minKPI', 'maxKPI');
    end

    % Save the min and max Entry for test data normalization
    if exist('minEntry', 'var')
        save(tmpdir + "MinMaxEntry.mat", 'minEntry', 'maxEntry');
    end

    % Save the min and max mu and sigma for test data normalization
    if exist('mu', 'var')
        save(tmpdir + "MuSig.mat", 'mu', 'sig');
    end

end