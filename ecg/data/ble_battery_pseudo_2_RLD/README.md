- CR2032 coin cell battery was used to power CC2540 and the ECG interface circuit.

- Sample rate = 400 Hz, 12 ENOB ADC
- Total gain = 6 (diff. gain) x 100 (single ended gain) = 600
- RLD gain = 200

- If a single battery is used to power the CC2540 and the analog circuitry, the noisy IR drop due to the digital circuitry causes severe noisea
- Use either two batteries (one for analog and one for digital).
- Try using a ferrite bead to separate analog and digital supplies or use a LDO or DC-DC converter to regulate the supply.
