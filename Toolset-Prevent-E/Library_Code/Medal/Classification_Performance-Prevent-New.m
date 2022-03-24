function TPs = Classification_Performance(tr_up, tr_dw, injection, fault, fileName, outDir, Anomalous_FE)

    % Number of the last time points to consider
    % history_cache = 3;
    history_cache = 1;
    % Number of TPs within the last time points to consider as a threshold
    % cache_sum_thr = 2;
    cache_sum_thr = 1;
    % Sum of TPs within the last [history_cache] time points
    cache_sum = 0;
    % set the time of the first TP to the time of filure
    firstTP = fault;
    % Cumulative number of TPs
    TP = 0;
    % Cumulative number of FPs
    FP = 0;
    
    history_list = [];
    TPs = [];

    for timestamp = 1:length(Anomalous_FE)
        % disp(["Timestamp", timestamp])
    
        if Anomalous_FE(timestamp) >= tr_up || Anomalous_FE(timestamp) <= tr_dw
            % Failure leading anomaly (FE Value is outside the normality
            % threshold)
            
            history_list(timestamp) = 1;
        
            if (timestamp >= history_cache) && ((timestamp < injection) || (timestamp >= injection + history_cache - 1))
                cache_sum = sum(history_list((timestamp - history_cache + 1) : timestamp));
            else
                cache_sum = 0;
            end

            
            if cache_sum >= cache_sum_thr
                % If faulty timestamp detected
                if timestamp < injection
                    % If fault detected before the failure injection
                    FP = FP + 1;
                else
                    % If fault detected after the failure injection
                    if timestamp < fault
                        % Fault detected after the injection, but before failure
                        TP = TP + 1;

                        % Set the time of detection of the firts TP
                        if firstTP == fault
                            firstTP = timestamp;
                        end

                        TPs = [TPs timestamp];
                        TPs = [TPs Anomalous_FE(timestamp)]; 
                    end
                end
            end

        else
            % Novelty (FE Value is inside the normality threshold)
            history_list(timestamp) = 0;
        end
    end

    minutes_before = fault - firstTP;
    FPR = FP / injection;
    if minutes_before ~= 0
        TTPR = (TP / minutes_before);
    else
        TTPR = 0;
    end

    TTPR = round(TTPR * 100);
    FPR = round(FPR * 100);

    writematrix(Anomalous_FE, outDir + "Anomalous_FE.csv")
    writematrix(history_list, outDir + "history_list_" + extractBefore(fileName,".mat") + ".csv")
    writematrix(TPs, outDir + "TPs.csv")

    outFilename = outDir + "Results" + ".csv";

    if isfile(outFilename)
        add_header = 0;
    else
        add_header = 1;
    end

    fileID = fopen(outFilename,'a+');
    if add_header
        fprintf(fileID, "%s, %s, %s, %s\n", "DataSet", "Minutes to failure", "T-TPR", "FPR");
    end
    fprintf(fileID, "%s, %d, %d, %d\n", extractBefore(fileName,".mat"), minutes_before, TTPR, FPR);
    fclose(fileID);

end