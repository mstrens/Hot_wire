# Hot_wire

This application runs on a PC and allows to control a CNC 4 axis hot wire in order to cut e.g. wings in foam.

This application is writen in Python 3 (and uses some Python packages) .
So, it is supposed to run on Windows, Linux and Mac
It uses a graphical user interface si is quite easy to use. 

The CNC has to run a 4 axis version of GRBL version 1.1
The easiest/cheapest solution for running GRBL is to use an arduino mega combined with a RAMP 1.x board.
A GRBL version running on this hardware is in the folder. It is a fork from GRBL made by ??? 

An alternative could be to use a version of GRBL running a STM32F103 (blue pill). This can be connected to a RAMP 1.x or directly to drivers like TB6600. Such a GRBL version is available on this Github site. 

In this python application you can
- define the characteristics of your table (dimension, speed, com port, baudrate, ...)
- define the characteristics of some material (high/low speeds, radiances, normal cutting speed)
- upload ".dat" files for root and tip profiles
- transform the profiles (chords, thickness, incidence, inverse, smoothing, reducing points, ...)
- define the dimensions and position of the bloc on the table
- directly control the CNC hot wire (connect to Grbl, unlock GRBL, Home, Move the 4 axis, make vertical/horizontal.inclined cuts, apply heat,...)
- generate and save the gcode for cutting the profiles in the foam
- send the generated gcode to GRBL
- save and reload previous projects, tables, materials

In order to run the application, you have to install:
- python 3 latest version ( I tested it with version 3.7)
- tkinter (normally already included in python)
- mathplotlib
- numpy
- configparser
- shapely
- scipy
- serial
- time  (normally already included in python)
- threading (normally already included in python)
- atexit (normally already included in python)
- queue (normally already included in python)

Here some screen shots

![Profil](https://github.com/mstrens/Hot_wire/blob/master/image/Cut.png)
