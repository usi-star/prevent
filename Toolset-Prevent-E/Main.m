%% Setting parameters
clear;

% Add path to functions that we're going to use
addpath('./Data/PreProcessing_Code/');
addpath('./Library_Code/Medal/');

% Numer of data's, Until now we have just 4 possibilities:
% 36, 158, 1540 and 1720 KPIs. We have injection time and fault time 
% just in datas having 1720 KPIs.
KPI = 1720;

% Setting the value for the trendline(s) to be plotted
Ks = [1, 2]; 

% Defines the preprocessing method(s) for data values allowed:
%
% - Stand: Standardization by column, in particular it's made by looping
%          each COLUMN (= KPIs) value and replacing each value as follows:
%          newValue = (oldValue - KPI_Mean)/ KPI_StndDev,
%
% - NormMatrix: Data-Scaling performed in order to have every value in
%               range [0, 1], done as follows:
%               newValue = (oldValue - minValueofMatrix)/ (maxValueofMatrix - minValueofMatrix),
%
% - NormKPI: Data-Scaling performed in order to have every value in
%            range [0, 1], done as follows:
%            newValue = (oldValue - minValueofColumn)/ (maxValueofColumn - minValueofColumn),
%
% - Raw: No preprocessing
preProc = ["Stand"];

% Insert every value(s) of Learning rate with which train the RBM, 
% typically a value between 0.1 and 0.0001
lr_to_test = [0.01]; 

% Directory in which store the final data after pre-processing
finalDataDir = "./Data/FinalData/";
if (exist(finalDataDir, 'dir') ~= 7)
    mkdir(finalDataDir);
end

% Directory in which raw data is stored
rawDirectory = "./Data/Raw_Data/";

% Directory in which store the final result,
% divided into two different directories:
% outDir/Csv (for Python) and outDir/Mat (for MatLab)
outDir = "./Result/";

% If outDir doesn't exist, create it
if (exist(outDir, 'dir') ~= 7)
    mkdir(outDir);
end

% Since plotting FE's graphs (in particular the one concerning the normal 
% data) requires a lot of time, you might consider to avoid its plotting
plotNormal = false;

%% Creation of the data

% Starting from folders containintg different files of different length,
% this step will unify them in a specified and unique dataset for each 
% fault tipology.
% realNumberofKPIs is required because the real numbers of KPI may change
% from our expectation if we're going to enable the eliminateStringColumn
% option.

% if true, displays operations step-by-step
debug = false;

% if true, during the pre-processing phase every string column will be
% discarded,
% if false, it will replace every string with a unique int, for example: 
% [ ['a', 'b', 'c'], ['b', 'e', 'a'] ] -> [ [1, 2, 3], [2, 4, 1] ]
eliminateStringColumn = true;

realNumberofKPIs = CreateDataFromRaw(KPI, rawDirectory, finalDataDir, preProc, eliminateStringColumn, debug);
%% Training RBM(s) and Plotting FE Distributions - MATLAB

% After the training of the RBM, a model based on FE's trendline will be
% used to evaluate the anomalous data.
% This step will also create one image containing the plotted FE Distribution in the outDir
% directory for each fault type of anomalous data.

if ~exist('realNumberofKPIs', 'var')
    realNumberofKPIs = KPI;
end

finalDataDirMat = finalDataDir + "Mat/"; 

for i = 1:length(preProc)
    for j = 1:length(lr_to_test)
        RBM_Train(finalDataDirMat, realNumberofKPIs, lr_to_test(j), outDir, preProc(i), plotNormal, Ks);
    end
end

disp("Finish");
