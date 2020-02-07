#!/usr/bin/env python
# filename:          serialConn.pyw
# kind:              Python file
# first created:     28.08.2012
# created by:        zas
################################################################################
# History:
# v0.1 : zas 28.08.2012
#
################################################################################
# Description: 
# Core for the Custom Serial Program
################################################################################
# Installation: 
# Module : python27, serial, serialutils
################################################################################
__author__ = "zas"
__date__   = "01.07.2012"

################################################################################
# Import modules
#

from serialutils import enumerate_serial_ports
import serial, os

import serial, serialutils

class serialConn():
  
    def __init__(self):
        """ Init Serial Port object """ 
        self.comReading = False
        self.recording = False
    
    def portOpen(self):
        return self.comReading
    
    def setRecord(self, recording):
        self.recording = recording
     
    def findPorts(self):
        """ Search for available Ports """
        com_port_combo = []
        for port in serialutils.enumerate_serial_ports(): 
            com_port_combo.append(port)
        return com_port_combo
        
    def openSerial(self, port , speed):
        """ Open given Port with a given Speed """
        try:
            self.ser = serial.Serial(str(port), int(speed))
            self.comReading=True
            return True
        except:
            return False
        
    def closeSerial(self):
        """ Close the open Serial Port """
        try:
            self.comReading=False
            self.ser.close()
            return True
        except:
            return False

    def sendCommand(self, command):
        """ Send command over the open Serial Port """
        try:
            self.ser.write( command )
            return True
        except:
            return False
            
    def receiving(self):
        """ Thread for receiving the Serial Commands """
        try:
          return self.ser.readline()
        except:
          return False

            