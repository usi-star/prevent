% Converting Gaetano's dataset to data format expected from RBM's Library
function AnomalousSet = AnomalousData(nKPI, method, Directory, faultType, eliminateStringColumn, debug)
    
    % Temporary directory in which store results like read dataset non processed
    % and min-max values, mean, standard deviation, ecc.
    tempDir = "./Data/PreProcessing_Code/tmp/";

    % Directory in which find the .csv files
    % (Unification process of multiple .csv)
    Files = dir(fullfile(Directory,'*.csv'));

    % Read the first .csv in the folder and save
    % its properties (dimensions, var names, ecc.)
    finalTest = readtable(fullfile(Directory, Files(1).name),'PreserveVariableNames',true);
    entries = size(finalTest);
    KPIs = finalTest.Properties.VariableNames;
    finalTest = finalTest(1:entries(1), 1:entries(2));

    % Read any other .csv in the folder
    for k = 2:length(Files)
        baseFileName = Files(k).name;
        fullFileName = fullfile(Directory, baseFileName);
        dataset = readtable(fullFileName,'PreserveVariableNames',true);        
        dataset.Properties.VariableNames = KPIs;
        entries = size(dataset);
        Testdata = dataset(1:entries(1), 1:entries(2));
        finalTest = [finalTest; Testdata];
    end
    
    
    if eliminateStringColumn
        S = vartype('numeric');
        finalTest = [finalTest(:, 1), finalTest(:,S)];        
    end
    
    entries = size(finalTest);

    % Order the final dataset according to the timestamp
    sortrows(finalTest, 'timestamp');
    
    % removing timestamps since they were useful just for guaranteeing a correct sorting
    % of the entries
    finalTest = finalTest(:, 2:entries(2));
    
    % The following code will convert any string column in a consistent
    % incremental numerical value, in order to be processed by the RBM
    if ~eliminateStringColumn
        entries = size(finalTest);
        newCols = [];
        colNames = [];
        indexCols = [];
        for i = 1:entries(2)
            % If a column contining string values is found, its index, name and
            % values are stored
            if iscellstr(finalTest(1, i).(1))
                indexCols = [ indexCols i ];
                newCols = [ newCols table2array(finalTest(:, i)) ];
                colNames = [ colNames finalTest.Properties.VariableNames(i) ];
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
            finalTest = addvars(finalTest,newCols(:, i), 'After', colName, 'NewVariableNames', "NewTMPColumn");
            finalTest(:, indexCols(i)) = [];
            finalTest.Properties.VariableNames(indexCols(i)) = colName;
        end
    end

    % Covert the result table in a matrix
    Testdata = table2array(finalTest);
    entries = size(Testdata);
    
    if debug
        disp("Unify Process finished - Anomalous Data");
    end
    
    % Unification Process termined

    %% Data preprocessing Phase
    
    if debug
        disp("Data Preprocessing Phase - Anomalous Data");
    end
    
    tmpDirPattern = tempDir + nKPI + "_";

    switch method
        case 'Stand'
            load(tmpDirPattern + "MuSig.mat", 'mu', 'sig');
            for i = 1:entries(2)
                entry = Testdata(:, i);
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
                Testdata(:, i) = entry;
            end

        case 'NormMatrix'
            load(tmpDirPattern + "MinMaxEntry.mat", 'minEntry', 'maxEntry');
            for i = 1:entries(1)
                current_row = Testdata(i, :);
                for j = 1:entries(2)
                    current_row(j) = (current_row(j) - minEntry) / (maxEntry - minEntry);
                    if isnan(current_row(j))
                        current_row(j) = 0;
                    end
                    if isinf(current_row(j))
                        current_row(j) = 1;
                    end
                end
                Testdata(i, :) = current_row;
            end

        case 'NormKPI'
            load(tmpDirPattern + "MinMaxKPI.mat", 'minKPI', 'maxKPI');
            % Apply the data Scaling
            for i = 1:entries(2)
                current_row = Testdata(:, i);
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
                Testdata(:, i) = current_row;
            end
            
        case "Raw"
            % Maintain the data as it is
    end

    %% Saving Phase

    % Save the new .csv file
    directory = "./Data/FinalData/Csv/";
    csvname = faultType + ".csv";
    out = directory + csvname;
    csvwrite(out, Testdata);
    AnomalousSet = out;
end