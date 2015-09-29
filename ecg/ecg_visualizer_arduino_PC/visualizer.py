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

import serial
import streamplot
import time

# data (12 bits) - byte oriented - first LSB, then MSB
# 2 LSB bits - 00 - LSB 6 bits
#              01 - MSB 6 bits
#              10 - debug out - 6 bits LSB
#              11 - debug out - 6 bits MSB
# waveform is reset when debug value of 4095 is sent

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0)
ser.flushInput()
ser.flush()

def numKeyPressCallBack(num):
    ser.write(str(num))

ecgPlot = streamplot.StreamPlot(saveFileNameStart = "ecg_plot",lines = [('l','r','ecg')], exitforce=True, numKeyPressCallBack=numKeyPressCallBack)

Tsample = 1e-3 # in second
printdebug = True


def uartread():
    serbuf = ""
    data = 0
    debugdata = 0
    t = 0

    while True:
        serbuf += ser.read(100000)
        for c in serbuf:
            val = ord(c)
            value = val & 0x3F
            valtype = val / 64
            if valtype == 0: # LSB
                data = value
            elif valtype == 1: # MSB
                data = data + value*64
                t += Tsample
                yield (t, data)
            elif valtype == 2: # debug LSB
                debugdata = value
            elif valtype == 3: # debug MSB
                debugdata += value*64
                if printdebug:
                    print "Debug data from device: ", debugdata
                if debugdata == 4095:
                    print "Got command to reset plot . . ."
                    t = 0
                    ecgPlot.resetPlot()
        serbuf = ""
        time.sleep(0.001)

for i in uartread():
    t, val = i
    ecgPlot.addDataPoint(t, [val])

