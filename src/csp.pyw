#!/usr/bin/env python
# filename:          csp.pyw
# kind:              Python file
# first created:     28.08.2012
# created by:        zas
################################################################################
# History:
# v0.1 : zas 28.08.2012
#
################################################################################
# Description: 
# Main Script to launch GUI for Custom UART Serial Command Programm
################################################################################
# Installation: 
# Module : python27 ,pyqt4, gui, serialutils, serial, serialConn
# Linux  : sudo apt-get install python2.7 python-qt4
################################################################################
__author__ = "zas"
__date__   = "28.08.2012"

import sys
from PyQt4 import QtGui
import gui
import ctypes

################################################################################
# Launch Window
#
if __name__ == "__main__":
    author  = 'zas'
    program = 'CSP'
    version = '1.9'
    appid = author + "." + program + "." + version
    # Only working in 64bit systems
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    # Someone is launching this directly
    # Create the QApplication
    app = QtGui.QApplication(sys.argv)
    # The Main window
    main_window = gui.MainUI(version, author, program)
    main_window.show()
    # Enter the main loop
    try:
        app.exec_()
    except:
        print "Unexpected error:", sys.exc_info()[0]
