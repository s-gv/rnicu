% Get ECG data from MIT-BIH database - http://www.physionet.org/physiobank/database/mitdb/
% Sample rate for all the MIT-BIH CSV files in this directory is 360 samples/sec
% y-axis is in mV

% WFDB for MATLAB needs to be installed for this to work
% Installation instructions here : http://www.physionet.org/physiotools/matlab/wfdb-app-matlab/

[tm,sig]=rdsamp('mitdb/234',1);
x = sig(1:25000);
plot(x);
%csvwrite('mit_bih_234.csv', x);