ECG
===

An electrocardiograph prototype for the Remote Neonatal Monitoring and Intervention Project.

Dependencies
------------

- Python 2.7
- Arduino >= 1.5.6-r2 (for Arduino Due)
- stream-plot (source included, but streamplot's dependencies need to be met) - https://github.com/s-gv/stream-plot
- MATLAB / Octave if you want to run simulations
- TI SmartRF Flash Programmer
- IAR 8051 >= 8.30 (only if you want to re-compile the source code for CC2540)
- TI CCDebugger (for programming CC2540)

How-to-use
----------

Wired ECG with Arduino:

- Build the circuit in `schematics/ecg_arduino.png`. A USB to UART converter such as FT232 or CP2102 may be used.
- Program the Arduino with the source in `ecg_arduino/ecg_arduino.ino`.
- Goto `ecg_visualizer_arduino_PC/` and run `python visualizer.py`. If the serial port name is incorrect, edit `visualizer.py`.
- Press the hi-z electrodes across the heart and press the RLD electrode to the leg or forehead. Alternatively, the outer ring of one of the hi-z electrodes can be connected to the RLD electrode. For more details, see the technical report in `report/ecg_tech_report.pdf`. You should now see an ECG signal on the PC display.
- Note that a laptop (with the power cord removed) must be used to power the Arduino. Preferably, keep the laptop on your lap. Interference will be much worse if a mains powered desktop is used; the interference may be so strong as to saturate the amplifiers leading to no useful ECG signal at all.

Wireless ECG with Bluetooth Low Energy (BLE using CC2540):

- Build the circuit in `schematics/ecg_CC2540.png`. A more complete schematic is in `schematics/ecg_CC2540_full.png`. Program the CC2540 in the circuit with the hex file `ecg_CC2540/hexfiles/SimpleBLEPeripheral.hex`.
- Connect the CC2540 USB dongle to a PC (either a laptop or a mains powered desktop will do). Program the CC2540 USB dongle with the hex file `ecg_CC2540/hexfiles/CC2540_USBdongle_HostTestRelease_All.hex`.
- Goto `ecg_visualizer_ble_PC/` and run `python visualizer.py`. If the serial port name is incorrect, edit `visualizer.py`.
- Press the hi-z electrodes across the heart and press the RLD electrode to the leg or forehead. Alternatively, the outer ring of one of the hi-z electrodes can be connected to the RLD electrode. For more details, see the technical report in `report/ecg_tech_report.pdf`. You should now see an ECG signal on the PC display. A sample recording may be found [here](https://github.com/s-gv/ecg/blob/master/data/ble_single_battery_LP5907_psuedo2_RLD/screenshots/screenshot0.png).
- Note that the CC2540, which is gathering ECG data and transmitting wirelessly, has to be powered by a battery (ex: CR2032 coin cell). If a mains power source is used, interference will be much worse.
