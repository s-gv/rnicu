- Heat shrinked cables are used to connect the electrodes to the PCB.
- Single CR2032 coin cell battery directly powers CC2540 (DVDD and AVDD)

- Battery -> LP5907 (1.8v regulator) -> ECG circuitry and AREF
- 12 bit (ENOB) ADC used at 400 Hz. 

- Two electrodes are placed across the heart and a PDMS layer (butterfly) sits between the electrodes and the skin
- RLD wire is held in the hand
- Diff gain (6) x Single ended gain (100) = 600
- In the CSV, y-val of 8191 corresponds to 1.8 v after gain and 3 mV before gain and y-val of 0 corresponds to 0 v

