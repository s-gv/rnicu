- The PCBs are wrapped in foam and placed inside the pocket of a runner's belt. Heat shrinked cables are used to connect the electrodes to the PCB.
- In one of the electrodes, the outer ring was connected to RLD
- Single CR2032 coin cell battery directly powers CC2540 (DVDD and AVDD)

- Battery -> LP5907 (1.8v regulator) -> ECG circuitry and AREF
- 12 bit (ENOB) ADC used at 400 Hz. 

- The two dry contact G=1 electrodes are placed on the sides of the abdomen
- Diff gain (6) x Single ended gain (100) = 600
- RLD gain = 200
- In the CSV, y-val of 8191 corresponds to 1.8 v after gain and 3 mV before gain and y-val of 0 corresponds to 0 v

- The drop in the amplitude in the CSV file ('screenshots/screenshot5.png') is because of a loose connection and may be ignored.
