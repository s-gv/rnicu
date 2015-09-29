%Copyright (C) 2014  Sagar G V (sagar.writeme@gmail.com)

%This program is free software: you can redistribute it and/or modify
%it under the terms of the GNU Affero General Public License as published by
%the Free Software Foundation, either version 3 of the License, or
%(at your option) any later version.

%This program is distributed in the hope that it will be useful,
%but WITHOUT ANY WARRANTY; without even the implied warranty of
%MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
%GNU Affero General Public License for more details.

%You should have received a copy of the GNU Affero General Public License
%along with this program.  If not, see <http://www.gnu.org/licenses/>.

% This script implements adaptive filtering to remove 50 Hz inteference
% as described in Martens et. al, "Improved Adaptive Line Canceller for
% Electrocardiography", IEEE Transactions on Biomedical Engg. The variable
% names correspond to the symbols used in the paper. 

clear all; close all;

%%%%%%%%%%%%%%%%%%%%%%%%%%
Fs = 400; % *dont* change without changing the error filter
N = 11000; % Num of samples. Keep above 11000.
%%%%%%%%%%%%%%%%%%%%%%%%%%
Ka = 1/(0.13 * Fs);
Kphi = 6e-2;
Kdw = 9e-4;
omegan_p = 2*pi*50/Fs; % nominal frequency. *dont* change without changing the error filter
eps = 1e-15; % epsilon
kx = 400; % threshold computation window
block_n = 40; % number of samples for which adaptation is blocked
%%%%%%%%%%%%%%%%%%%%%%%%%%
Ts = 1/Fs;
t = (1:N)'*Ts; % time

% 2nd order butterworth error filter. fc = 80 Hz, Fs = 400 Hz. 
% Gain at 50 Hz = 1
b = [1.266 -2.532 1.266]; % error filter numerator
a = [1 -0.3695 0.1958]; % error filter denominator
hcomb = [0.5 0 0 0 0 0 0 0 -0.5];

%s = csvread('../visualizer/ecg_plot_0.csv'); %0.5*ones(size(t));% original signal
%s = s(3000:3000+max(size(t))-1);
%x = 2*sin(2*pi*49*t); % corrupt signal
%x(7000:8000) = 2*sin(2*pi*51*Ts*(7000:8000));
%x(9000:10000) = 3*sin(2*pi*49*Ts*(9000:10000));


%d = x + s; % corrupt signal
d = csvread('../data/custom_2_diff/ecg_plot_1.csv');
d = d(:,2);

e = zeros(size(d)); % error signal (cleaned signal)
ew = zeros(size(d)); % filtered error signal
dh = zeros(size(d)); % corrupt signal filtered by comb filter
x_est = zeros(size(d)); % inteference estimate

ymod_phi = zeros(size(d));
ymodw_phi = zeros(size(d)); % filtered signature
ymod_a = zeros(size(d));
ymodw_a = zeros(size(d)); % filtered signature

osc_i = zeros(size(d));
osc_q = zeros(size(d));

thetaa_est = zeros(size(d));
thetaphi_est = zeros(size(d));
thetadw_est = zeros(size(d));
adap_supp = zeros(size(d));
thresh = zeros(size(d));

eta_a = zeros(size(d));
eta_phi = zeros(size(d));
alpha = zeros(size(d));

% set initial values
alpha(1) = 1;

for k=1:max(size(d))-1
    % do work
    osc_i(k) = sin(omegan_p * k + thetaphi_est(k));
    osc_q(k) = cos(omegan_p * k + thetaphi_est(k));
    
    x_est(k) = thetaa_est(k) * osc_i(k);
    
    e(k) = d(k) - x_est(k);
    ew(k) = b(1) * e(k); % high pass filter the error (desired) signal
    for it=2:max(size(a))
        if (k-it+1) > 0
            ew(k) = ew(k) + b(it)*e(k - it + 1) - a(it)*ew(k - it + 1);
        end
    end
    
    ymod_phi(k) = alpha(k) * osc_q(k);
    ymodw_phi(k) = b(1) * ymod_phi(k); % high pass filter the signature
    for it=2:max(size(a))
        if (k-it+1) > 0
            ymodw_phi(k) = ymodw_phi(k) + b(it)*ymod_phi(k - it + 1) - a(it)*ymodw_phi(k - it + 1);
        end
    end
    eta_phi(k) = 2*ew(k)*ymodw_phi(k);
    
    ymod_a(k) = osc_i(k);
    ymodw_a(k) = b(1) * ymod_a(k); % high pass filter the signature
    for it=2:max(size(a))
        if (k-it+1) > 0
            ymodw_a(k) = ymodw_a(k) + b(it)*ymod_a(k - it + 1) - a(it)*ymodw_a(k - it + 1);
        end
    end
    eta_a(k) = 2*ew(k)*ymodw_a(k);
    
    % update estimates
    thetaa_est(k+1) = thetaa_est(k);
    thetadw_est(k+1) = thetadw_est(k);
    thetaphi_est(k+1) = thetaphi_est(k) + thetadw_est(k);
    
    thetaa_est_new = thetaa_est(k) + Ka * eta_a(k);
    thetadw_est_new = thetadw_est(k) + Kdw * eta_phi(k);
    thetaphi_est_new = thetaphi_est(k) + Kphi * eta_phi(k) + thetadw_est(k);
    
    
    % should adaptation be suppressed ?
    l = round(block_n/2);
    if (k+l) <= max(size(dh))
        for it=1:max(size(hcomb))
            if (k+l - it + 1) > 0
                dh(k+l) = dh(k+l) + hcomb(it) * d((k+l) - it + 1);
            end
        end
        for it=0:kx-1
            if k+l - it > 0
                thresh(k+l) = thresh(k+l) + dh(k+l - it)^2;
            end
        end
        thresh(k+l) = 2 * (thresh(k+l)/kx)^0.5;
        if abs(dh(k+l)) > thresh(k+l)
            for it=0:2*l
                if (k+it) <= max(size(dh))
                    adap_supp(k+it) = 1;
                end
            end
        end
    end
    
    
    % perform adaptation if needed
    if adap_supp(k) == 0
        if thetaa_est_new > 0
            thetaa_est(k+1) = thetaa_est_new;
        end

        if abs(thetadw_est_new) < 4*2*pi/Fs
            thetadw_est(k+1) = thetadw_est_new;
        end
        thetaphi_est(k+1) = thetaphi_est_new;
    end
    
    if abs(thetaa_est(k+1)) > eps
        alpha(k+1) = 1/thetaa_est(k+1);
    end
    
end

%figure;plot(s,'b');title('original signal');
%figure;plot(x,'r');title('Interference signal');
figure;plot(d','k');title('corrupt signal');
figure;plot(e,'b');title('filtered signal');
%figure;plot(dh); hold on; plot(thresh,'k'); plot(adap_supp,'r');
