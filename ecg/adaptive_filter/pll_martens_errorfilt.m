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
% Adaptation supression are not implemented.

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
%%%%%%%%%%%%%%%%%%%%%%%%%%
Ts = 1/Fs;
t = (1:N)'*Ts; % time

% 2nd order butterworth error filter. fc = 80 Hz, Fs = 400 Hz. 
% Gain at 50 Hz = 1
b = [1.266 -2.532 1.266]; % error filter numerator
a = [1 -0.3695 0.1958]; % error filter denominator

s = 10*ones(size(t)) + 0.2*sin(2*pi*2*t); % original signal
x = 2*sin(2*pi*49*t); % corrupt signal
x(1:1000) = 0;
x(3000:4000) = 2*x(3000:4000);
x(6000:7000) = 2*sin(2*pi*51*Ts*(6000:7000));
x(end-1000:end) = 0;

d = x + s; % corrupt signal

e = zeros(size(d)); % error signal (cleaned signal)
ew = zeros(size(d)); % filtered error signal
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

eta_a = zeros(size(d));
eta_phi = zeros(size(d));
alpha = zeros(size(d));

% set initial values
alpha(1) = 1;

for k=1:N-1
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
    thetaphi_est(k+1) = thetaphi_est(k);
    
    if (thetaa_est(k) + Ka * eta_a(k)) > 0
        thetaa_est(k+1) = thetaa_est(k) + Ka * eta_a(k);
    end
    if abs(thetadw_est(k) + Kdw * eta_phi(k)) < 4*2*pi/Fs
        thetadw_est(k+1) = thetadw_est(k) + Kdw * eta_phi(k);
    end
    thetaphi_est(k+1) = thetaphi_est(k) + Kphi * eta_phi(k) + thetadw_est(k);
    if abs(thetaa_est(k+1)) > eps
        alpha(k+1) = 1/thetaa_est(k+1);
    end

end

figure;plot(s,'k');title('original signal');
figure;plot(x,'r');title('Interference signal');
figure;plot(d','k');title('corrupt signal');
figure;plot(e,'b');title('filtered signal');

