function CsvToMat(finalDataDir, nKPI, method, Set, Kind, faultType)
    
    % Converting Gaetano's dataset to data format expected from RBM's Library
    finalDataDir = finalDataDir + "Mat/";
    if (exist(finalDataDir, 'dir') ~= 7)
        mkdir(finalDataDir);
    end

    set = readtable(Set);
    if Kind == "Normal"
        Normal = table2array(set);
        save(finalDataDir + "training_dataset.mat", 'Normal');
    else
        filename = faultType + ".mat" ;
        Anomalous = table2array(set);
        switch faultType
            case "e1"
                injection = 91;
                fault = 126;
            case "e2"
                injection = 109;
                fault = 297;
            case "e3"
                injection = 66;
                fault = 107;
            case "e4"
                injection = 31;
                fault = 105;
            case "e5"
                injection = 54;
                fault = 69;
            case "e6"
                injection = 56;
                fault = 132;
            case "e7"
                injection = 33;
                fault = 49;
            case "e8"
                injection = 42;
                fault = 140;
            case "e9"
                injection = 55;
                fault = 97;
            case "normal_w3"
                injection = 0;
                fault = 0;
            otherwise
                % Do nothing
        end
        if exist('injection', 'var') && exist('fault', 'var')
            save(finalDataDir + filename, 'Anomalous', 'injection', 'fault');
        else
            save(finalDataDir + filename, 'Anomalous');
        end
    end
end
