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
% names correspond to the symbols used in the paper. Error filtering and
% adaptation supression are not implemented.

clear all; close all;

%%%%%%%%%%%%%%%%%%%%%%%%%%
Fs = 400; % Sample rate
N = 7000; % Num of samples. Keep above 7000.
%%%%%%%%%%%%%%%%%%%%%%%%%%
Ka = 1/(0.13 * Fs);
Kphi = 6e-2;
Kdw = 9e-4;
omegan_p = 2*pi*50/Fs; % nominal frequency
eps = 1e-15; % epsilon
%%%%%%%%%%%%%%%%%%%%%%%%%%

Ts = 1/Fs;
t = (1:N)'*Ts; % time

% the corrupt signal is initially 0. Then a 49 Hz sine starts, its
% amplitude steps up, down. Afterwords, the frequency changes abruptly to
% 51 Hz with an amplitude step. Subsequently, the frequency changes back to
% 49 Hz with an amplitude step. Finally, the interference drops to 0.
d = 2*sin(2*pi*49*t); % corrupt signal
d(1:400) = 0;
d(2000:3000) = 2*d(2000:3000);
d(4000:5000) = 3*sin(2*pi*51*Ts*(3000:4000));
d(end-1000:end) = 0;

e = zeros(size(d)); % error signal (cleaned signal)
x_est = zeros(size(d)); % inteference estimate

ymod_phi = zeros(size(d));
ymod_a = zeros(size(d));

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
    
    ymod_phi(k) = alpha(k) * osc_q(k);
    eta_phi(k) = 2*e(k)*ymod_phi(k);
    
    ymod_a(k) = osc_i(k);
    eta_a(k) = 2*e(k)*ymod_a(k);
    
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

plot(d','r');title('corrupt signal');
figure;
plot(e);title('filtered signal');

