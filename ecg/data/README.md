ECG data
========

- MIT-BIH database - http://www.physionet.org/physiobank/database/mitdb/
- Sample rate for all the MIT-BIH CSV files in this directory is 360 samples/sec
- y-axis is in `mV`
- Each MIT-BIH CSV file has about the first 1 minute of the database on the website.

- Scripts for synthesizing ECG waveforms (in synth/) was downloaded from here : http://www.physionet.org/physiotools/ecgsyn/
- Sample rate is included in the file name (ex: 512 samples/sec)

How to get data from Physionet
------------------------------

WFDB for MATLAB needs to be installed to get ECG data from Physionet, the online database. Installation instructions here : http://www.physionet.org/physiotools/matlab/wfdb-app-matlab/
