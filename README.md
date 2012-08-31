[Custom Serial Program](zawiki.dyndns.org/~zas/zawiki/doku.php/tschinz:myprograms) - UART Debug Monitor
================================

The goal is to facilitate the debug of a system with the help of a serial. This program lets you create custom commands and they can be sent over a Serial Port. The record of the send and received commands can be create with a appropriate timestamp.
---
To Launch the Program you need to have installed Python 2.7 and certain modules.
- [Python 2.7.x](http://www.python.org/getit/releases/2.7/)
- [PyQt4](http://www.riverbankcomputing.co.uk/software/pyqt/download) from Riverbank
- [Py2Exe](http://www.py2exe.org/) only used for creating a Windows exectuable

For launching do `python csp.pyw` or double click on the file. You need to have the above installed

Usage
---
### Linux

For Linux launch, user the `csp.pyw` script in the `scr` folder. All the above modules need to be installed.
`sudo apt-get install python2.7 python-qt4 python-py`

### Windows
For launching on Windows an executable wsa build. Launch the `csp.exe` in the `bin` folder.

Python based
---
All scripts are entirely python based and intented for Python 2.X but also "compatible" with Python 3.X although there is no support on it.
The program should work on Linux, but it wasn't tested.

Sourcefiles
---
- csp.pyw is the main script launcher
- gui.py creates the GUI and its elements
- serialConn.py handles the serial connection (need module serial)
- serialutils.py handles low level serial commands
- setup2exe.py creates automatically a Windows executable


Licensing
---
This document is under the [CC BY-NC-ND 3-0 License, Attribution-NonCommercial-NoDerivs 3.0 Unported](http://creativecommons.org/licenses/by-nc-nd/3.0/).

