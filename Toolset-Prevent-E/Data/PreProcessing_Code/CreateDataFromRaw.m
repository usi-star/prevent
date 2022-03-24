function realNumberofKPIs = CreateDataFromRaw(nKPI, rawDirectory, finalDataDir, preProc, eliminateStringColumn, debug)
    %% Defining parameters for the data creation phase

    normalDir = rawDirectory + "training_dataset";
    anomalousDir = rawDirectory;
    allowedAnomalousDir = ["e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9", "normal_w3"];

    %% Data creation phase

    for i = 1:length(preProc)
        [NormalSet, Real_KPIs] = NormalData(nKPI, preProc(i), normalDir, finalDataDir, eliminateStringColumn, debug);
        CsvToMat(finalDataDir, Real_KPIs, preProc(i), NormalSet, "Normal");
        for j = 1:length(allowedAnomalousDir)
            AnomalousSet = AnomalousData(Real_KPIs, preProc(i), (anomalousDir + allowedAnomalousDir(j)), allowedAnomalousDir(j), eliminateStringColumn, debug);
            CsvToMat(finalDataDir, Real_KPIs, preProc(i), AnomalousSet, "Anomalous", allowedAnomalousDir(j));
        end
    end
    
    realNumberofKPIs = Real_KPIs;
end
