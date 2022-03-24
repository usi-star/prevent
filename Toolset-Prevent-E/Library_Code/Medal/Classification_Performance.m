function TPs = Classification_Performance(tr_up, tr_dw, fileName, outDir, FE)

    outDir = "./Output/";
    outDir_ma = "./Output_ma/";
    
    HISTORY_CACHE = 3;
    CACHE_SUM_THR = 2;

    history_list = [];
    predictions_ma_list = [];

    for timestamp = 1:length(FE)
        history_list(timestamp) = 0;
        predictions_ma_list(timestamp) = 0;

        % FE Value outside the normal threshold
        if FE(timestamp) >= tr_up || FE(timestamp) <= tr_dw
            history_list(timestamp) = 1;

            cache_sum = 0;
            if (timestamp >= HISTORY_CACHE)
                cache_sum = sum(history_list((timestamp - HISTORY_CACHE + 1) : timestamp));
            end

            if cache_sum >= CACHE_SUM_THR % Faulty timestamp detected
                predictions_ma_list(timestamp) = 1;
            end
        end
    end

    file_name = strrep(fileName,'mat','csv');
    
    disp(file_name);
    
    history_list_final = zeros(length(history_list),1);
    predictions_ma_list_final = zeros(length(predictions_ma_list),1);

    for ii = 1:length(history_list_final)
        history_list_final(ii) = history_list(ii);
    end
    
    for ii = 1:length(predictions_ma_list_final)
        predictions_ma_list_final(ii) = predictions_ma_list(ii);
    end
    
    % save the prediction history without moving average
    writematrix(history_list_final, outDir + file_name)
    
    % save the prediction history with moving average
    writematrix(predictions_ma_list_final, outDir_ma + file_name)
    

    % save the prediction history with moving average
    % outFilename = outDir + "predictions_ma.csv";
    % fileID = fopen(outFilename,'a+');
    % for timestamp = 1:length(predictions_ma_list)
    %     fprintf(fileID, "%d\n", predictions_ma_list(timestamp));
    % end
    % fclose(fileID);
    
    TPs = [];

end