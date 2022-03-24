function RBM_Train(finalDataDirMat, nodes, learning_rate, outDir, preProc, plotNormal, Ks)

% K-value for final trendline estimation and classification of
% anomalous data, the suggested values are [1, 4], but in order to
% choose the best k-value you should analyze the output of the normal
% data's FE
kforClassification = 1;

% RBM's most important parameters
batchSz = 15;
epoch = 20;

% Load the training dataset (the .mat file converted from .csv file)
load(finalDataDirMat + "training_dataset.mat");

% Setting a random seed for RBM's sampling
seed = 42;
rng(seed);

% Setting RBM's parameter as declared in Main.m
arch = struct('size', [nodes, nodes], 'inputType', 'binary');
opts = {'lRate',learning_rate, ...
    'batchSz',batchSz, ...
    'nEpoch',epoch, ...
    'wPenalty',25, ...
    'sparsity',5, ...
    'sparseFactor',10, ...
    'displayEvery',100};
arch.opts = opts;

% Initalization of the RBM
r = rbm(arch);

% RBM training
tic;
trained_rbm = r.train(Normal);
trainingTime = toc;
disp(trainingTime);

disp("RBM model trained. ");

%% Plotting and Saving Normal dataset(s)

color = ["k", "[0.9290, 0.6940, 0.1250]", "[0, 0.5, 0]", "y"];

tic;
% Computing FE for each timestamp
disp("Computing normal data's FE");
[normal_data_size, ~] = size(Normal);
Normal_FE = zeros(1, normal_data_size);
for i = 1:normal_data_size
    fe_tmp = trained_rbm.freeEnergy(Normal(i, :));
    Normal_FE(i) = fe_tmp;
end

% Trendline estimation
disp("Trendline Estimation");
median_FE = median(Normal_FE, 'all');
stnd_dev_FE = std(Normal_FE);
trendlines = [];
for k = 1:length(Ks)
    trendline_up = median_FE + (Ks(k) * stnd_dev_FE);
    trendline_dw = median_FE - (Ks(k) * stnd_dev_FE);
    trendlines = [trendlines trendline_up];
    trendlines = [trendlines trendline_dw];
end

% Plot the result of the baseline Model
if plotNormal
    disp("Plotting Normal Data's FE");
    pngNameNormal = outDir + extractBefore(fileNormal, ".mat") + "_lr_" + learning_rate + ".png";
    
    x = 1:normal_data_size;
    figure
    hold all
    FE_plot = plot(x, Normal_FE, 'DisplayName','Free-Energy');
    threshold_plot = [];
    index = 1;
    tr = 1;
    while index <= (length(trendlines)/2)
        p = yline(trendlines(tr), 'color', color(index), 'DisplayName', "k = " + Ks(index), 'LineWidth', 1.25);
        threshold_plot = [threshold_plot p];
        yline(trendlines(tr + 1), 'color', color(index), 'LineWidth', 1.25);
        tr = tr + 2;
        index = index + 1;
    end
    legend([FE_plot, threshold_plot], 'Location', 'North');
    hold off
    title('FE Distribution');
    xlabel('Timestamp');
    ylabel('Free-Energy');
    print('-dpng', '-r600', pngNameNormal);
end

%% Plotting and Saving Anomalous dataset(s)

Files = dir(fullfile(finalDataDirMat, "*.mat"));
for i = 1:length(Files)
    fileName = Files(i).name;
    
    if fileName == "training_dataset.mat"
        continue
    end

    pathToFile = fullfile(finalDataDirMat, fileName);
    load(pathToFile);
    
    % Computing FE data
    [anomalous_data_size, ~] = size(Anomalous);
    Anomalous_FE = zeros(1, anomalous_data_size);
    for j = 1:anomalous_data_size
        fe_tmp = trained_rbm.freeEnergy(Anomalous(j, :));
        Anomalous_FE(j) = fe_tmp;
    end
    
    % Analysis of the Anomalous FE for the final classification, just
    % if the values fault and injection was inserted in the dataset
    % setting also title's name since it's also related to the existance
    % of those variables
    titleName = 'FE Distribution';
    if exist('injection', 'var') && exist('fault', 'var')
        % titleName = " Injection at " + num2str(injection) + ", Fault at " + num2str(fault);
        tr_up = median_FE + (kforClassification * stnd_dev_FE);
        tr_dw = median_FE - (kforClassification * stnd_dev_FE);
        % TPs = Classification_Performance(tr_up, tr_dw, injection, fault, fileName, outDir, Anomalous_FE);
        TPs = Classification_Performance(tr_up, tr_dw, fileName, outDir, Anomalous_FE);
    end
    
    % Plotting results
    x = 1:anomalous_data_size;
    figure
    hold all
    xticks(0:15:anomalous_data_size);
    FE_plot = plot(x, Anomalous_FE, 'DisplayName','Free-Energy');
    threshold_plot = [];
    index = 1;
    tr = 1;
    while index <= (length(trendlines)/2)
        p = yline(trendlines(tr), 'color', color(index), 'DisplayName', "k = " + Ks(index), 'LineWidth', 1.25);
        threshold_plot = [threshold_plot p];
        yline(trendlines(tr + 1), 'color', color(index), 'LineWidth', 1.25);
        tr = tr + 2;
        index = index + 1;
    end
    
    % Plot lines representing the fault and injection time just if we have those values in the data
    if exist('injection', 'var') && exist('fault', 'var')
        xline(injection, 'g', {'Injection'});
        xline(fault, 'r', {'Failure'});
        single = 1;
        pair = 1;
        if length(TPs) > 1
            TP_plot = plot(TPs(single), TPs(single+1), 'ro', ...
                'DisplayName', 'Fault Detected');
            while pair <= length(TPs)/2
                plot(TPs(single), TPs(single+1), 'ro');
                single = single + 2;
                pair = pair + 1;
            end
        end
    end
    
    if exist('TPs', 'var') && length(TPs) > 1
        legend([FE_plot, threshold_plot, TP_plot], 'Location', 'North');
    else
        legend([FE_plot, threshold_plot], 'Location', 'North');
    end
    
    hold off
    
    % Setting title of each plot and its axes
    title(titleName);
    xlabel('Timestamp');
    ylabel('Free-Energy');
    
    % Saving each result in the out directory
    fileName = extractBefore(fileName,".mat");
    pngNameAnomalous = outDir + fileName + "_lr_" + learning_rate + ".png";
    print('-dpng', '-r600', pngNameAnomalous);
end
end