close all; clear all;

disp('------------------------------------------------------------------');
disp('------------------------------------------------------------------');

tRec = 60; % duration of recording
%filename_end = 'min1_25bpm.csv';
filename_end = 'min2_24bpm.csv';
%filename_end = 'min3_22bpm.csv';
%filename_end = 'min4_24bpm.csv';
%filename_end = 'min5_25bpm.csv';
%filename_end = 'min6_23bpm.csv';
%filename_end = 'min7_23bpm.csv';
%filename_end = 'min8_21bpm.csv';

imuData = csvread(strcat('../data/long_term_lying_down_10mins/cleaned_imu_', filename_end));
imu_fs = 100; % imu sampling frequency in Hz

ecgData = csvread(strcat('../data/long_term_lying_down_10mins/cleaned_ecg_', filename_end));
ecg_fs = 400; % ecg sampling frequency in Hz

plot((1:size(imuData, 1))/size(imuData, 1) * tRec, imuData(:, 3));
hold on;
plot((1:size(ecgData, 1))/size(ecgData, 1) * tRec, 6000 + ecgData(:, 2), 'r');
xlabel('time (second)');
legend('IMU', 'ECG');

ecg_hi = conv(ecgData(:, 2), [1 -1]);
ecg_hi = ecg_hi(1:end-1); ecg_hi(1) = 0;
figure; plot(ecgData(:,2)); hold on;
ecg_std = std(ecg_hi);
ecg_hi_thresh = (ecg_hi > 3*ecg_std);
ecg_hi_thresh_rising = (ecg_hi_thresh - [0; ecg_hi_thresh(1:end-1)]) > 0;
%hold on; plot(ecg_hi_thresh_rising * 2000, 'k');
p_time = find(ecg_hi_thresh_rising == 1);
qrs_amps = zeros(size(p_time));
for it=1:size(p_time,1)
    start = max([p_time(it)-20 1]);
    stop = min([p_time(it)+20 max(size(ecgData))]);
    range = start:stop;
    qrs_amps(it) = max(ecgData(range, 2)) - min(ecgData(range, 2));
end
qrs_amps_resampled = interp1(p_time, qrs_amps, 1:size(ecgData,1), 'spline');
%plot(p_time, qrs_amps, 'k');
plot(qrs_amps_resampled, 'r');
qrs_amps_resampled_f = abs(fft(qrs_amps_resampled));
qrs_amps_resampled_f(1) = 0;
%figure; plot(qrs_amps_resampled_f);

br_filt_l = 0.1;
br_filt_h = 0.5;
br_filt_range = round(br_filt_l/ecg_fs*max(size(qrs_amps_resampled))):round(br_filt_h/ecg_fs*max(size(qrs_amps_resampled)));
ecgbrfft = abs(fft(qrs_amps_resampled));
ecgbrfft(br_filt_range) = 0;
ecgbrfft(end+2-br_filt_range) = 0;
ecgbrfft = abs(fft(qrs_amps_resampled)) - ecgbrfft;
%figure; plot(ecgbrfft);

p2p_time = conv(p_time, [1 -1]);
p2p_time = p2p_time(2:end-1);
p_time = p_time(2:end);
%figure; plot(p_time, p2p_time);
avg_heart_rate = mean( 60 ./ (p2p_time/ecg_fs) )
%figure;plot((1:size(ecg_hi, 1))/size(ecg_hi, 1) * tRec, ecg_hi_thresh_rising * 12000, 'k');


imufft = abs(fft([imuData(:, 3)]));
imuffth = imufft(2:ceil(end/2));

peakloc = find(imuffth == max(imuffth));
imu_breathing_est = peakloc * imu_fs/2 / size(imuffth, 1) * 60

peakloc = find(ecgbrfft == max(ecgbrfft));
ecg_dr_breathing_est = peakloc(1) * ecg_fs / max(size(ecgbrfft)) * 60