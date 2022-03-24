function RBM_Train(finalDataDirMat, nodes, learning_rate, outDir, preProc, plotNormal, Ks)

% K-value for final trendline estimation and classification of
% anomalous data, the suggested values are [1, 4], but in order to
% choose the best k-value you should analyze the output of the normal
% data's FE
kforClassification = 1;

% Consider every anomalous set linked to the normal data?
testEveryAnomalousData = true;

% RBM's most important parameters
batchSz = 15;
epoch = 20;

% Which fault type you want to estimate
faultType = "e1"; % Allowed : Exp_91, Linear_109, Random_6, Generic_150, e*X*

% Selecting normal data, anomalous data patterns
fileAnomalous = "Anomalous_" + nodes + "_" + preProc + "_" + faultType + ".mat";
fileNormal = "Normal_" + nodes + "_" + preProc + ".mat";

% Load the .mat file converted from .csv file
load(finalDataDirMat + fileNormal);

disp(finalDataDirMat + fileNormal);
disp(Normal);

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

% cprintf('comment', "RBM Successfully Trained");
disp("RBM Successfully Trained");
disp(" ");

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

tr_up = median_FE + (kforClassification * stnd_dev_FE);
tr_dw = median_FE - (kforClassification * stnd_dev_FE);
Classification_Performance(tr_up, tr_dw, outDir, Normal_FE);

% Plot the result of the baseline Model
pngNameNormal = outDir + extractBefore(fileNormal, ".mat") + "_lr_" + learning_rate + ".png";
if plotNormal
    disp("Plotting Normal Data's FE");
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