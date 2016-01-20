stream-plot
===========

A data visualization tool for streaming data. It is based on Galry, an open-source tool by Cyrille Rossant.


Features
---------

- Auto-focus. As streaming data gets displayed, the plot pans and zooms appropriately and fits the data to the screen.
- Key press triggers the program to save the last n samples acquired

Dependencies
-----------

- Python 2.7 - http://www.python.org/
- Open GL >= 2.1 - Your graphics drivers should support OpenGL 2.1
- PyOpenGL >= 3.0.2 - http://pyopengl.sourceforge.net/
- PyQt4 with openGL bindings - http://www.riverbankcomputing.com/software/pyqt/download
- NumPy - http://www.numpy.org/
- matplotlib - http://matplotlib.org/


stream-plot uses Galry 0.1.0.rc1 ( http://rossant.github.io/galry/ ) which is bundled in the form of source code. You don't need to download/install Galry separately.

Note: On Ubuntu 12.04, you can install all dependencies with `apt-get install python-opengl python-qt4 python-qt4-gl python-numpy python-scipy python-matplotlib`

How to use
----------

- Install all dependencies.
- Clone this project
- See src/streamplot_test*.py for examples. Run "python src/streamplot_test2.py" in the command line.
- To use stream-plot in your own project, include the file 'src/streamplot.py' and folders 'src/galry' and 'src/qtools' in the root of your script.

Shortcuts
---------

When the plot figure is in focus, the following shortcuts may be used.

- 'a' - Toggle auto-focus
- 'd' - Save the last n samples into a csv file
- 'f' - Save all buffered samples into a csv
- 'z' - Zoom-in along the time axis
- 'x' - Zomm-out along the time axis
- 'c' - Save samples visible on screen to a csv

The entire list of available shortcuts may be seen by pressing 'h' when the window is in focus.
