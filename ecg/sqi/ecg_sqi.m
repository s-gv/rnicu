function [ op ] = ecg_sqi( data, Fs )
% fs is the sampling frequency in Hz
% data is the ECG data series. 
% op is 0-5 (0 being the best and 5 being the worst)

FS= Fs; %Sampling Frequency
CH= 1;
WIN=FS*3;
START= FS*1;

%Threshold values 
MAX_AMP = 2000;
MAX_DIFF = 400; 
BAD_AROUND_SPIKE = 5;
	
MAX_WRONG_AMP = 1800;
MAX_WRONG_DIFF = 1800;
MAX_CONSTANT = 3600;
MAX_BAD = 4000;
N_X_MAX = 49;
CHAN_DIST = 2000;
	
%Define Quality values 
GOOD = 0;
BAD =  1;
AMP =  2;
DIFF =  3;
CONST =  4;
CROSS =  5;
	
good_samples = zeros(WIN-START,1);

result = GOOD;


n_wrong_amp = 0;
n_wrong_diff = 0;
n_constant = 0;
n_bad = 0;
n_x_this_chan = 0;

good_samples = ones(WIN-START,1);

for it=1:WIN-START
    val = data(it+START);
    prev_val = data(it+START-1);
    
    if abs(val - prev_val) > MAX_DIFF
        for jt = max(it-BAD_AROUND_SPIKE,1):it+BAD_AROUND_SPIKE
            if jt < WIN-START
                if good_samples(jt) == 1
                    n_wrong_diff = n_wrong_diff + 1;
                    n_bad = n_bad + 1;
                    good_samples(jt) = 0;
                end
            end
        end
    elseif abs(val) > MAX_AMP
        n_wrong_amp = n_wrong_amp + 1;
        good_samples(it) = 0;
        n_bad = n_bad + 1;
    elseif val == prev_val
        n_constant = n_constant + 1;
        n_bad = n_bad + 1;
        good_samples(it) = 0;
    end
    
    if n_bad > MAX_BAD
        op = BAD;
        return;
    end
    if n_wrong_amp > MAX_WRONG_AMP
        op = AMP;
        return;
    end
    if n_wrong_diff > MAX_WRONG_DIFF
        op = DIFF;
        return;
    end
    if n_constant > MAX_CONSTANT
        op = CONST;
        return;
    end
    
    
end


op = result;

end

