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

# create a stream plot containing two channels. First one shown by a solid red line and the second one by a solid blue line
myPlot = streamplot.StreamPlot(saveFileNameStart = "my_plot",lines = [('l','r','redPlot'),('l','b','bluePlot')])

# add two data points
myPlot.addDataPoint( 0 , [99,98] ) # at time t=0, channel 0 has y-value 99 and channel 1 has y-value 98
myPlot.addDataPoint( 1 , [50,38] ) # at time t=1, channel 0 has y-value 50 and channel 1 has y-value 38

# wait for the user to hit the exit button on the GUI
myPlot.waitUntilExit()