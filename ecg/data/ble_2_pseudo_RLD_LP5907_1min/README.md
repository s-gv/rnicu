- A CR2032 battery powered wireless ECG monitor.
- The two electrodes were pressed vertically across the heart.
- The RLD output was connected to the outer ring of one of the electrodes.
- In the CSV file, the first column is time in seconds and the second column is the ADC reading at that time.

- ADC: 14 bit (12-bit ENOB). ADC value 0 => 0v; ADC value 8191 => 1.8v; ADC value -8192 => -1.8v;
- Sampling rate: 400 Hz. 
- ECG Signal gain = 606. 
- RLD gain = 200. 
- Considering the signal gain, the ECG signal is 0.3626 uV/bit at the ADC output. 

