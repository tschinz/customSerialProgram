[Custom Serial Program](http://zawiki.dyndns.org/~zas/zawiki/doku.php/tschinz:myprograms) - UART Debug Monitor
================================

The goal is to facilitate the debug of a system with the help of a serial. This program lets you create custom commands and they can be sent over a Serial Port. The record of the send and received commands can be create with a appropriate timestamp.

---
                   
![CSP Screennshot](http://zawiki.praxis-arbor.ch/lib/exe/fetch.php/tschinz:programming:programs:csp:screenshot_csp.png)

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
For launching on Windows an executable was build. Launch the `csp.exe` in the `bin` folder.

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

Changelog
---
- 1.8   - added setting.ini and choosable *.cmd file
- 1.7.3 - Created win32 and win64 binaries
- 1.7.2 - fixed GUI reception bug
- 1.7.1 - new Button layout and text
- 1.7   - Added loop function, seperate Thread for sending
- 1.6   - Add \n\r & decoding, improved add remove command
- 1.5   - Added Reset button and Menubar
- 1.4   - Bugfix stability issue
- 1.3   - Opening closing port automatic
- 1.2   - Icons modified
- 1.1   - Bugfix automatic scrolling
- 1.0   - First official Relase
- 0.3   - Release, non Public
- 0.2   - Release, non Public
- 0.1   - Initial Release, non Public

Licensing
---
This document is under the [CC BY-NC-ND 3-0 License, Attribution-NonCommercial-NoDerivs 3.0 Unported](http://creativecommons.org/licenses/by-nc-nd/3.0/).

