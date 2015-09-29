'''
This program visualizes ECG waveforms on the PC

Copyright (C) 2014  Sagar G V (sagar.writeme@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import CC2540ble as ble
import streamplot

def main():
    print "Connecting to BLE Dongle . . ."
    bt = ble.BTDongle(port='/dev/ttyACM0')

    print "Discovering BLE devices in the vicinity . . ."
    devs = bt.discover()
    print "BLE Devices found: ", devs

    print "Changing conncection parameters . . ."
    bt.changeConnectionSettings()

    print "Establishing link to the first device found . . ."
    print bt.link(devs[0])

    print "Enabling notifications . . ."
    print bt.enableNotifications('0x002F')

    ecgPlot = streamplot.StreamPlot(saveFileNameStart = "ecg_plot",lines = [('l','r','ecg')], exitforce=True)
    ecgPlot.addDataPoint(0, [0])
    Tsample = 1/400.0 # in seconds
    t = 0


    for evt in bt.pollNotifications():
        if len(evt) == 16:
            f2s = lambda x: x if x < 2**13 or x >= 65530 else (-2**14 + x)
            vals = [ f2s(lsb + 256*msb) for (lsb, msb) in zip(evt[::2], evt[1::2]) ]
            vals = [ val for val in vals if val < 65530 ]
            for val in vals:
                t += Tsample
                ecgPlot.addDataPoint(t, [val])

if __name__ == '__main__':
    main()
