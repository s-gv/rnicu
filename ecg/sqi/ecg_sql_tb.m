close all; clear all;

data = csvread('../data/ble_single_battery_LP5907_psuedo2_RLD/ecg_plot_1.csv');
data = data(:,2);
fs = 400; % sampling frequency

disp('------------------------------------------');
%data = sin(2*pi*1*(1:10000)/fs);
disp(ecg_sqi(data, fs));

plot(data);