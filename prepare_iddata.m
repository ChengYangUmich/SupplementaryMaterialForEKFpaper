function [z, ze, zv] = prepare_iddata(filename)

excel_name = filename;
%%%%%%%%%%%% load SNH and TSS
opts = spreadsheetImportOptions("NumVariables", 3);
% Specify sheet and range
opts.Sheet = "InputD";
opts.DataRange = "D5:F1013";

% Specify column names and types
opts.VariableNames = ["QRAS","QMLE","QPE"];
opts.VariableTypes = ["double","double", "double"];

% Import the data
state = readtable(excel_name, opts, "UseExcel", false);
QRAS = state{:,"QRAS"};
QMLE = state{:,"QMLE"};
QPE = state{:,'QPE'};

%%%%%%%%%%%% TKN
opts = spreadsheetImportOptions("NumVariables", 1);
% Specify sheet and range
opts.Sheet = "Influent";
opts.DataRange = "E5:E1013";

% Specify column names and types
opts.VariableNames = "TKN";
opts.VariableTypes = "double";

% Import the data
orange = readtable(excel_name, opts, "UseExcel", false);
TKN = orange{:,"TKN"};

%%%%%%%%%%%% Time
opts = spreadsheetImportOptions("NumVariables", 1);
% Specify sheet and range
opts.Sheet = "TSS";
opts.DataRange = "B5:B1013";

% Specify column names and types
opts.VariableNames = ["Time"];
opts.VariableTypes = ["double"];

% Import the data
orange = readtable(excel_name, opts, "UseExcel", false);
Time = orange{:,"Time"};

%%%%%%%%%%%% MLSS
opts = spreadsheetImportOptions("NumVariables", 1);
% Specify sheet and range
opts.Sheet = "Biomass";
opts.DataRange = "D5:D1013";

% Specify column names and types
opts.VariableNames = ["MLSS"];
opts.VariableTypes = ["double"];

% Import the data
orange = readtable(excel_name, opts, "UseExcel", false);
MLSS = orange{:,"MLSS"};

%%%%%%%%%%%% load SO's
opts = spreadsheetImportOptions("NumVariables", 3);
% Specify sheet and range
opts.Sheet = "DO";
opts.DataRange = "C5:E1013";

% Specify column names and types
opts.VariableNames = ["SO1", "SO2","SO3"];
opts.VariableTypes = ["double", "double", "double"];

% Import the data
input = readtable(excel_name, opts, "UseExcel", false);
SO1 = input{:,"SO1"};
SO2 = input{:,"SO2"};
SO3 = input{:,"SO3"};

%%%%%%%%%%%% load SNH's
opts = spreadsheetImportOptions("NumVariables", 3);
% Specify sheet and range
opts.Sheet = "SNH";
opts.DataRange = "D5:F1013";

% Specify column names and types
opts.VariableNames = ["SNH1", "SNH2","SNH3"];
opts.VariableTypes = ["double", "double", "double"];

% Import the data
input = readtable(excel_name, opts, "UseExcel", false);
SNH1 = input{:,"SNH1"};
SNH2 = input{:,"SNH2"};
SNH3 = input{:,"SNH3"};


%% Transform the data into iddata
total_num_points = length(Time); 
train_evaluation_ratio = 0.5; 
n = floor(total_num_points*train_evaluation_ratio);

% TSS's is normalized to kg/m3
% COD_in is also normalized to kg/m3
y = [SNH1 SNH2 SNH3];
u = [QPE QRAS QMLE TKN MLSS SO1 SO2 SO3];

z = iddata(y, u, 1/24/6, 'Name', 'true data'); % Ts = 10 minutes
z.TimeUnit = 'days';

ze = z(1:n);
zv = z(n+1:end);

end

