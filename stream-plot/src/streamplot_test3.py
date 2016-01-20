''' stream-plot is a data visualization tool for streaming data. It is based on Galry by Cyrille Rossant.
    Copyright (C) 2013  Sagar G V 
    E-mail : sagar.writeme@gmail.com

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

import streamplot
import time

# create a stream plot containing two channels. First one shown by a solid red line and the second one by blue dots
myPlot = streamplot.StreamPlot(saveFileNameStart = "my_plot",lines = [('l','r','redPlot'),('o','b','bluePlot')],legend=True, exitforce=True)

def run():
	t = 0
	while True:
		#a ramp-up
		if t==400:
			t = 0
			myPlot.resetPlot()
		for i in range(100):
			time.sleep(0.05)
			myPlot.addDataPoint(t, [i,i+2]) # addDataPoint( time , [y_val_channel_0 , y_val_channel_1] )
			t += 1

		#the signal stays constant
		for i in range(100):
			time.sleep(0.05)
			myPlot.addDataPoint(t, [99,96])
			t += 1

run()
