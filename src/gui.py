#!/usr/bin/env python
# filename:          gui.py
# kind:              Python file
# first created:     01.06.2012
# created by:        zas
################################################################################
# History:
# v0.1 : zas 01.07.2012
#
################################################################################
# Description: 
# GUI to for Custom UART Serial Command Programm
################################################################################
# Installation: 
# Module : python27 ,pyqt4, csp
# Linux  : sudo apt-get install python2.7 python-qt4
################################################################################
__author__ = "zas"
__date__   = "01.07.2012"

################################################################################
# Import modules
#
import sys, os, re, time
import PyQt4
from PyQt4 import QtGui, Qt
from PyQt4 import QtCore
from threading import Thread
from multiprocessing import Process
import serialConn
import time

################################################################################
# Constants
#
indent = '  '
titel = "CSP - Custom Serial Program"
windowsize = (700,600)
verbosity = False
port_default = 0
baudrates = [100, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 56000, 57600, 115200, 128000, 256000]
baudrate_default = 12
terminations = [["None", ""], ["CR", "\r"], ["LF", "\n"], ["CR+LF", "\r\n"]]
termination_default = 3
command_file = "commands.cmd"
temp_file = "temp.txt"
history_file = "history.txt"
send_command_history_size = 10
timestamp_interval = 5
loop_time = 1000
loop_nbr = 1


class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, icon, parent)
        self.menu = QtGui.QMenu(parent)
        exitAction = self.menu.addAction("Exit")
        self.setContextMenu(self.menu)

################################################################################
# Define gui class
class MainUI(QtGui.QMainWindow):
    """ This is the main class for the GUI of the Custom Serial Program """
    
    def __init__(self, version, author, program,  win_parent = None):
        # Constructor
        QtGui.QMainWindow.__init__(self, win_parent)
        self.command_file = command_file
        self.init_UI()

        # Connect Thread Signals
        self.connect(self, QtCore.SIGNAL("data_received"), self.writeCommand)

        # Load settings
        self.settings = QtCore.QSettings('./settings.ini', QtCore.QSettings.IniFormat)
        self.loadSettings()
        
        self.version = version
        self.author  = author
        self.program = program
        
    def __del__(self):
        # Deconstructor
        """ Close Ports and Files and Quit Application """
        if self.portOpen:
            self.toggle_port()
        if self.recording:
            self.toggle_record()

        self.connect(self, QtCore.SIGNAL("please_killme"), QtCore.SLOT("close()"))
        self.emit(QtCore.SIGNAL("please_killme"))
        self.saveSettings()

    #=============================================================================
    # Function definitions of class
    #
    def loadSettings(self):
        """ Reads all setting values from the .ini file """
        i = 0
        for port in self.ports:
            if port == self.settings.value("uart/port").toString():
                self.com_port_combo.setCurrentIndex(i)
                break
            i = i + 1
        
        i = 0
        for baudrate in baudrates:
            if baudrate == self.settings.value("uart/baudrate").toInt()[0]:
                self.com_speed_combo.setCurrentIndex(i)
                break
            i = i + 1
        
        self.com_term_combo.setCurrentIndex(self.settings.value("uart/termination").toInt()[0])
        self.command_file = self.settings.value("files/command").toString()
        self.cmdfile_label.setText(os.path.split(str(self.command_file))[1])
        self.update_commands()
        history_file = self.settings.value("files/history")
        self.com_send_edit.setMaxCount(self.settings.value("send/send_history").toInt()[0])
        timestamp_interval = self.settings.value("send/timestamp_interval").toInt()[0]
        self.loop_time_spin.setValue(self.settings.value("send/loop_interval").toInt()[0])
        self.loop_nbr_spin.setValue(self.settings.value("send/loop_nbr").toInt()[0])

    def saveSettings(self):
        """ Saves all setting values from the .ini file """
        self.settings.beginGroup("uart")
        self.settings.setValue("port", self.com_port_combo.currentText())
        self.settings.setValue("baudrate", baudrates[self.com_speed_combo.currentIndex()])
        self.settings.setValue("termination", self.com_term_combo.currentIndex())
        self.settings.endGroup();
        self.settings.beginGroup("files")
        self.settings.setValue("command",self.command_file)
        self.settings.setValue("history",history_file)
        self.settings.endGroup();
        self.settings.beginGroup("send")
        self.settings.setValue("send_history",send_command_history_size)
        self.settings.setValue("timestamp_interval",timestamp_interval)
        self.settings.setValue("loop_interval",self.loop_time_spin.value())
        self.settings.setValue("loop_nbr",self.loop_nbr_spin.value())
        self.settings.endGroup();

    def init_UI(self):
        """ Initialise UI, creates all GUI elements """
        # variable
        self.verbosity = 0
        self.recording = False
        self.serialConn = serialConn.serialConn()
        self.lastTime = time.localtime()
        self.firstTime = True
        self.portOpen = False
        self.sending = False
        
        ####
        # Tray Icon
        #
        trayIcon = SystemTrayIcon(QtGui.QIcon("icons/csp.png"))
        #trayIcon.show()
        
        ####
        # Toolbar
        #
        self.toggleport = QtGui.QAction(QtGui.QIcon('icons/open.png'), 'Open/Close Port', self)
        self.toggleport.setShortcut('Ctrl+P')
        self.connect(self.toggleport, QtCore.SIGNAL('triggered()'), self.toggle_port)
        
        self.rst = QtGui.QAction(QtGui.QIcon('icons/clean.png'), 'Clean Terminal', self)
        self.rst.setShortcut('Ctrl+Shift+R')
        self.connect(self.rst, QtCore.SIGNAL('triggered()'), self.reset)
        
        self.record = QtGui.QAction(QtGui.QIcon('icons/record.png'), 'Start/Stop Record', self)
        self.record.setShortcut('Ctrl+S')
        self.connect(self.record, QtCore.SIGNAL('triggered()'), self.toggle_record)
        
        self.info = QtGui.QAction(QtGui.QIcon('icons/info.png'), 'Info', self)
        self.info.setShortcut('Ctrl+I')
        self.connect(self.info, QtCore.SIGNAL('triggered()'), self.displayInfo)
        
        self.help = QtGui.QAction(QtGui.QIcon('icons/help.png'), 'Help', self)
        self.help.setShortcut('Ctrl+H')
        self.connect(self.help, QtCore.SIGNAL('triggered()'), self.displayHelp)
        
        self.exit = QtGui.QAction(QtGui.QIcon('icons/exit.png'), 'Exit', self)
        self.exit.setShortcut('Ctrl+Q')
        self.connect(self.exit, QtCore.SIGNAL('triggered()'), self.__del__)
        
        left_spacer = QtGui.QWidget()
        left_spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        
        # Create Toolbar
        self.toolbar = self.addToolBar('Actions')
        self.toolbar.addAction(self.toggleport)
        self.toolbar.addAction(self.rst)
        self.toolbar = self.addToolBar('Record')
        self.toolbar.addAction(self.record)
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addWidget(left_spacer)
        self.toolbar.addAction(self.help)
        self.toolbar.addAction(self.info)
        self.toolbar.addAction(self.exit)
        
        # Create Menubar
        self.menubar = self.menuBar()
        actionMenu = self.menubar.addMenu('&Actions')
        actionMenu.addAction(self.toggleport)
        actionMenu.addAction(self.rst)
        actionMenu.addAction(self.record)
        elseMenu = self.menubar.addMenu('&Else')
        elseMenu.addAction(self.info)
        elseMenu.addAction(self.help)
        elseMenu.addAction(self.exit)
        
        self.displayMainContent()
    # END init_UI
    
    def displayMainContent(self):
        """ Generates Main GUI, display Main Content of the program """
        ####
        # Widgets
        #
        # Title label
        self.script_label = QtGui.QLabel(titel)
        
        # Input Parameters
        # Port
        self.com_port_label = QtGui.QLabel("Port")
        self.com_port_combo = QtGui.QComboBox()
        self.ports = self.serialConn.findPorts()
        i = 0
        for port in self.ports:
            self.com_port_combo.insertItem(i, port)
            i = i + 1
        self.com_port_combo.setCurrentIndex(port_default)
        
        # Baudrate
        self.com_speed_label = QtGui.QLabel("Speed")
        self.com_speed_combo = QtGui.QComboBox()
        self.com_speed_combo.setEditable(True)
        i = 0
        for baudrate in baudrates:
            self.com_speed_combo.insertItem(i, str(baudrate))
            i = i + 1
        self.com_speed_combo.setCurrentIndex(baudrate_default)
        
        # Termination
        self.com_term_label = QtGui.QLabel("Termination")
        self.com_term_combo = QtGui.QComboBox()
        self.com_term_combo.insertItem(0, terminations[0][0], terminations[0][1])
        self.com_term_combo.insertItem(1, terminations[1][0], terminations[1][1])
        self.com_term_combo.insertItem(2, terminations[2][0], terminations[2][1])
        self.com_term_combo.insertItem(3, terminations[3][0], terminations[3][1])
        self.com_term_combo.setCurrentIndex(termination_default)

        # UART output (with scrollbar)
        self.uartBox = QtGui.QTextEdit("Script Output")
        self.uartBox.setReadOnly(True)
        self.uartBox.setFont(QtGui.QFont("Consolas"))
        self.uartscrollbar = self.uartBox.verticalScrollBar()
        self.uartscrollbar.triggerAction(QtGui.QScrollBar.SliderToMaximum)
        
        # Command box
        self.cmdfile_label = QtGui.QLabel(self.command_file)
        self.cmdfile_button = QtGui.QPushButton("Browse")
        self.commandBox = QtGui.QListWidget()
        self.reload_button = QtGui.QPushButton("")
        self.reload_button.setIcon(QtGui.QIcon('icons/reset.png'))
        self.reload_button.setToolTip("Refresh")
        self.add_button = QtGui.QPushButton("")
        self.add_button.setIcon(QtGui.QIcon('icons/add.png'))
        self.add_button.setToolTip("Add")
        self.min_button = QtGui.QPushButton("")
        self.min_button.setIcon(QtGui.QIcon('icons/min.png'))
        self.min_button.setToolTip("Delete")
        
        # UART Box textchanged connect
        QtCore.QObject.connect(self.uartBox,
                               QtCore.SIGNAL("textChanged()"),
                               self.uartBox_changed)

        # Browse Command File button
        QtCore.QObject.connect(self.cmdfile_button,
                       QtCore.SIGNAL("clicked()"),
                       self.browseFile)
        
        # Command List Double click connect
        QtCore.QObject.connect(self.commandBox,
                               QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"),
                               self.list_send_command)
        
        # Reload button connect
        QtCore.QObject.connect(self.reload_button,
                               QtCore.SIGNAL("clicked()"),
                               self.update_commands)
        # Add button connect
        QtCore.QObject.connect(self.add_button,
                               QtCore.SIGNAL("clicked()"),
                               self.add_command)
        # Min button connect
        QtCore.QObject.connect(self.min_button,
                               QtCore.SIGNAL("clicked()"),
                               self.min_command)
        
        # Command send
        self.com_send_label = QtGui.QLabel("Command:")
        self.com_send_edit   = QtGui.QComboBox()
        self.com_send_edit.setEditable(True)
        self.com_send_edit.setMaxCount(send_command_history_size)
        self.com_send_edit.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.com_send_button = QtGui.QPushButton("Send")
        self.com_send_button.setFocus()
        self.com_send_button.setDisabled(True)
        self.com_send_button.setIcon(QtGui.QIcon('icons/send.png'))
        self.com_send_button.setToolTip("Send")
        
        # Loop function
        self.loop_time_label_1 = QtGui.QLabel("Loop every")
        self.loop_time_label_1.setFixedHeight(24)
        self.loop_time_spin = QtGui.QSpinBox()
        self.loop_time_spin.setMinimum(1)
        self.loop_time_spin.setMaximum(999999)
        self.loop_time_spin.setValue(loop_time)
        self.loop_time_spin.setAlignment(QtCore.Qt.AlignRight)
        self.loop_time_label_2 = QtGui.QLabel("ms")
        self.loop_time_label_2.setFixedHeight(24)
        self.loop_nbr_spin = QtGui.QSpinBox()
        self.loop_nbr_spin.setMinimum(1)
        self.loop_nbr_spin.setMaximum(999999)
        self.loop_nbr_spin.setValue(loop_nbr)
        self.loop_nbr_spin.setAlignment(QtCore.Qt.AlignRight)
        self.loop_nbr_label_2 = QtGui.QLabel("times")
        self.loop_nbr_label_2.setFixedHeight(24)

        # Send button connect
        QtCore.QObject.connect(self.com_send_button,
                               QtCore.SIGNAL("clicked()"),
                               self.line_send_command)
        # Line Edit Return Connect
        QtCore.QObject.connect(self.com_send_edit.lineEdit(),
                               QtCore.SIGNAL("returnPressed()"),
                               self.line_send_command)
        
        # Layout
        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(self.com_port_label)
        hbox1.addWidget(self.com_port_combo)
        hbox1.addWidget(self.com_speed_label)
        hbox1.addWidget(self.com_speed_combo)
        hbox1.addWidget(self.com_term_label)
        hbox1.addWidget(self.com_term_combo)
        hbox1.addStretch(1)
        
        vbox1 = QtGui.QVBoxLayout()
        hbox1_0 = QtGui.QHBoxLayout()
        hbox1_0.addWidget(self.cmdfile_label)
        hbox1_0.addWidget(self.cmdfile_button)
        vbox1.addLayout(hbox1_0)
        vbox1.addWidget(self.commandBox)
        hbox1_1 = QtGui.QHBoxLayout()
        hbox1_1.addWidget(self.reload_button)
        hbox1_1.addWidget(self.add_button)
        hbox1_1.addWidget(self.min_button)
        vbox1.addLayout(hbox1_1)
        command_widget = QtGui.QWidget()
        command_widget.setLayout(vbox1)
        
        # Splitter (for resizing the UART output and the Commandbox)
        splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.uartBox)
        splitter.addWidget(command_widget)
        splitter.setSizes([windowsize[0]*0.75, windowsize[0]*0.25])
        hbox2 = QtGui.QHBoxLayout()
        hbox2.addWidget(splitter)
        
        hbox3 = QtGui.QHBoxLayout()
        hbox3.addWidget(self.com_send_label)
        hbox3.addWidget(self.com_send_edit)
        #hbox3.addWidget(self.com_send_button)

        hbox4 = QtGui.QHBoxLayout()
        hbox4.addStretch(1)
        hbox4.addWidget(self.loop_time_label_1)
        hbox4.addWidget(self.loop_time_spin)
        hbox4.addWidget(self.loop_time_label_2)
        hbox4.addWidget(self.loop_nbr_spin)
        hbox4.addWidget(self.loop_nbr_label_2)
        hbox4.addSpacing(24)
        hbox4.addWidget(self.com_send_button)
        hbox4.setSizeConstraint(QtGui.QLayout.SetFixedSize)


        main_layout = QtGui.QVBoxLayout()
        main_layout.addLayout(hbox1)
        main_layout.addLayout(hbox2)
        main_layout.addLayout(hbox3)
        main_layout.addLayout(hbox4)
        
        # Create central widget, add layout and set
        main_widget = QtGui.QWidget()
        main_widget.setLayout(main_layout)
        self.winCenter()
        
        # set Windows infos
        self.setWindowTitle(titel)
        self.setWindowIcon(QtGui.QIcon('icons/logo.png'))
        self.statusBar().showMessage('Ready')
        self.resize(windowsize[0], windowsize[1])
        
        self.setCentralWidget(main_widget)
        
        self.update_commands()
    # END DisplayMainContent
    
    def update_commands(self):
        """ Reads command file and adds to the commandBox """
        self.commands = []
        self.read_commands()
        self.commandBox.clear()
        for i in self.commands:
            self.commandBox.addItem(i.rstrip())
        self.statusBar().showMessage('Read ' + self.command_file)
    # END update_command
    
    def write_commands(self):
        """ Reads the commandbox and write all commands into the command file"""
        if os.path.isfile(self.command_file):
            f = open(self.command_file, "w")
            filedata = ""
            for row in range(self.commandBox.count()):
                f.write(str(self.commandBox.item(row).text()) + "\n")
            f.close()
        else:
            self.statusBar().showMessage('Error: File ' + self.command_file  + ' doesnt exist')
    # END write_command
    
    def read_commands(self):
        """ Reads command file and puts the content in the command List"""
        if os.path.isfile(self.command_file):
            f = open(self.command_file, "r")
            file = f.readlines()
            for line in file:
                # remove comments
                line = re.sub("(--|#|//).*","",  line)
                #line.rstrip('\n\r')
                if line.strip():
                    self.commands.append(line) 
            f.close()
        else:
            self.statusBar().showMessage('Error: File ' + self.command_file  + ' doesnt exist')
    # END read_command

    def add_command(self):
        """ Lets adding an element to the command list """
        if self.com_send_edit.lineEdit().displayText().isEmpty():
            self.statusBar().showMessage('Error: No command given')    
        else:
            if not(self.commandBox.currentRow() == None):
                self.commandBox.insertItem(self.commandBox.currentRow()+1, self.com_send_edit.lineEdit().displayText())
                self.commandBox.setCurrentRow(self.commandBox.currentRow()+1)
            else:
                self.commandBox.insertItem(self.commandBox.count(), self.com_send_edit.lineEdit().displayText())
            self.write_commands()
            self.statusBar().showMessage('Ready: Added command ' + self.com_send_edit.lineEdit().displayText())
    # END add_command
    
    def min_command(self):
        """ Deletes an element from the command list """
        if not (self.commandBox.currentItem() == None):
            deleted_item =self.commandBox.takeItem(self.commandBox.currentRow())
            del deleted_item
            self.write_commands()
            self.statusBar().showMessage('Ready: Add command: ' + self.command_file)
        else:
           self.statusBar().showMessage('Error: No command selected')
    # END min_command

    def list_send_command(self, listItem):
        """ Receives QListWidgetItem and send command """
        if self.sending:
            self.sending = False
            self.sendingProcess.terminate()
            self.sendingProcess.join()
            self.com_send_button.setDisabled(True)
            self.com_send_button.setIcon(QtGui.QIcon('icons/send.png'))
            self.com_send_button.setText("Send")
            self.statusBar().showMessage('Ready: Sending stopped')
        else:
            if self.serialConn.portOpen():
                self.send_command(listItem.text())
            # Add send command to ComboBox History
            self.com_send_edit.insertItem(0, listItem.text())
            self.com_send_edit.setCurrentIndex(0)
    # END list_send_command
                
    def line_send_command(self):
        """ Receives QLineEdit and send command """
        if self.sending:
            self.sending = False
            self.sendingProcess.terminate()
            self.sendingProcess.join()
            self.com_send_button.setDisabled(True)
            self.com_send_button.setIcon(QtGui.QIcon('icons/send.png'))
            self.com_send_button.setText("Send")
            self.statusBar().showMessage('Ready: Sending stopped')
        else:
            if self.serialConn.portOpen():
                self.send_command(self.com_send_edit.lineEdit().text())
            # Add send command to ComboBox History
            self.com_send_edit.insertItem(0, self.com_send_edit.lineEdit().text())
            self.com_send_edit.setCurrentIndex(0)
    # END line_send_command
           
    def send_command(self, command):
        """ Sends command over UART"""
        # Add line termination and send
        command = str(command).decode("string_escape") #convert \n to newline

        if command :
            # if already sending
                self.sending = True
                self.com_send_button.setText("Stop")
                self.com_send_button.setIcon(QtGui.QIcon('icons/close.png'))
                #self.sendingProcess = Process(target=self.sender(command))
                #self.sendingProcess.start()
                # bugfix that py2exe doens't start new gui
                #self.sendingProcess.terminate()
                #self.sendingProcess.join()
                self.sendingThread = Thread(target=self.sender(command))
                self.sendingThread.start()
                #self.sendingThread.join()
        else :
            self.statusBar().showMessage('Error: No Command given')
    # END send_command
    
    def sender(self, command):
        for i in range(1, self.loop_nbr_spin.value()+1):
            if self.sending == False:
                break
            if self.serialConn.sendCommand(command + self.com_term_combo.itemData(self.com_term_combo.currentIndex()).toString()):
                self.statusBar().showMessage('Ready: Command  ' + str(i) + '/' + str(self.loop_nbr_spin.value()) + ' sent')
                self.emit(QtCore.SIGNAL("data_received"), command, True)
            else:
                self.statusBar().showMessage('Error: Command ' + str(i) + '/' + str(self.loop_nbr_spin.value()) + ' not sent')
                break
            if self.loop_nbr_spin.value() > 1 and i < self.loop_nbr_spin.value()+1:
              time.sleep(self.loop_time_spin.value()/1000)
        self.sending = False
        self.com_send_button.setIcon(QtGui.QIcon('icons/send.png'))
        self.com_send_button.setText("Send")
    # END sender        

    def writeCommand(self, command, send_nRecv):
        """ Write command into UARTBox and Historyfile if necessary """
        # Add timestamp if necessary
        if (time.mktime(time.localtime()) - time.mktime(self.lastTime)) > timestamp_interval or self.firstTime:
            self.firstTime = False
            timestamp = 15*indent + time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
            self.lastTime = time.localtime()
        else: 
            timestamp = ""
        
        # display in UARTBox window
        if timestamp:
            self.uartBox.setTextColor(QtGui.QColor("black"))
            self.uartBox.append(timestamp)
        if send_nRecv:
            self.uartBox.setTextColor(QtGui.QColor("blue"))
        else:
            self.uartBox.setTextColor(QtGui.QColor("red"))
        self.uartBox.append(command)
        time.sleep(0.01)
        # write to history file
        if self.recording:
            command = "\n" + command
            if os.path.isfile(history_file):
                f = open(history_file, "a")
                if timestamp:
                    timestamp = "\n" + timestamp
                    f.write(timestamp)
                f.write(command)
                f.close()
            else:
                self.statusBar().showMessage('Error: File ' + history_file  + ' doesnt exist')
    # END writeCommand
    
    def uartBox_changed(self):
        """ As soon as some lines where added to the Box, it will be scrolled down to the end """
        # Scroll down
        self.uartscrollbar.triggerAction(QtGui.QScrollBar.SliderToMaximum)
    # END uartBox_changed
    
    def browseFile(self):
        """ Opens browse Window for choosing a file """
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '', "Command files (*.cmd);;All files (*)")
        self.cmdfile_label.setText(os.path.split(str(filename))[1])
        if not(filename == '' and os.path.splitext(str(filename))[1] == "*.cmd"):
            self.command_file = str(filename)
            self.update_commands()
            self.statusBar().showMessage('Ready: File OK')
        else:
            self.statusBar().showMessage('Error: File NOK')
    # END browseFile
    
    def browseDir(self):
        """ Opens browse Window for choosing a directory """
        dirname = QtGui.QFileDialog.getExistingDirectory(self, 'Open directory', '')
        self.in_folder_edit.setText(dirname)
        if not(dirname == ''):
            self.statusBar().showMessage('Ready: Directory OK')
        else:
            self.statusBar().showMessage('Error: Directory NOK')
    # END browseDir
    
    def toggle_port(self):
        """ Open or Close Serial port """
        if self.portOpen:
            # Close Serial port
            if self.serialConn.closeSerial():
                self.portOpen = False
                self.statusBar().showMessage('Ready: Closed port ' + self.com_port_combo.currentText())
                self.com_speed_combo.setEnabled(True)
                self.com_port_combo.setEnabled(True)
                self.com_send_button.setDisabled(True)
                self.toggleport.setIcon(QtGui.QIcon('icons/open.png'))
                self.firstTime = True
            else:
                self.statusBar().showMessage('Error: Close port ' + self.com_port_combo.currentText())
        else:
        # Open Serial port
          if self.serialConn.openSerial(self.com_port_combo.currentText(), int(self.com_speed_combo.currentText())):
              # Start Receiving Thread
              self.receivingThread = Thread(target=self.receiving).start()
              self.portOpen = True
              self.statusBar().showMessage('Ready: Opened port ' + self.com_port_combo.currentText())
              self.com_speed_combo.setDisabled(True)
              self.com_port_combo.setDisabled(True)
              self.com_send_button.setEnabled(True)
              self.toggleport.setIcon(QtGui.QIcon('icons/close.png'))
          else:
              self.statusBar().showMessage('Error: Open port ' + self.com_port_combo.currentText())
    # END toggle_port

    def toggle_record(self):
        """ Toggle logging terminal """
        if self.recording:
            self.recording = False
            self.firstTime = True
            self.record.setIcon(QtGui.QIcon('icons/record.png'))
            self.statusBar().showMessage('Ready: Stop record in file ' + history_file)
        else:
            self.recording = True
            self.firstTime = True
            if os.path.isfile(history_file):
                f = open(history_file, "a")
                f.write("\n\n----- NEW SESSION @ " + time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + " -----")
                f.close()
                self.record.setIcon(QtGui.QIcon('icons/recording.png'))
                self.statusBar().showMessage('Ready: Start recording in file ' + history_file )
            else:
                self.statusBar().showMessage('Error: File ' + history_file  + ' doesnt exist')
        self.serialConn.setRecord(self.recording)
    # END toggle_record

    def reset(self):
        """ Reset All Fields of the GUI """
        self.update_commands()
        self.uartBox.clear()
        self.com_send_edit.clear()
        
        # again find ports
        index_old = self.com_port_combo.currentIndex()
        self.com_port_combo.clear()
        self.ports = self.serialConn.findPorts()
        i = 0
        for port in self.ports:
            self.com_port_combo.insertItem(i, port)
            i = i + 1
        self.com_port_combo.setCurrentIndex(index_old)
        
        self.statusBar().showMessage('Ready: Fields reset')
    # END reset
    
    def receiving(self):
        """ function for seperate Thread to receive incomming Messages """
        while self.serialConn.portOpen():
            recv_data = self.serialConn.receiving()
            if recv_data:
                self.emit(QtCore.SIGNAL("data_received"), recv_data[:-1], False)
    # END receiving
    
    def displayHelp(self):
        """ Display an Help information Dialog """
        self.statusBar().showMessage('Ready: Open Help dialog')
        QtGui.QMessageBox.information(self, self.program + " Help", "Custom Serial Program Help\n\n    1. First read the README.md\n\n    2. Learn by doing\n\n    3. Check with the author\n\n\nThis programm lets you open a serial (UART) connection and send predefined, as well as custom made commands over the serial connection. The predefined command can be added over the plus and minus button or written directly into the commands.txt file. The recorded history will be saved in the history.txt file.\n\nThanks for using " + self.program + ", your awesome!\n\n\t\t\t\t\t\t" + self.author)
    # END Displayinfo
    
    def displayInfo(self):
        """ Display an About me information Dialog """
        self.statusBar().showMessage('Ready: Open Info dialog')
        QtGui.QMessageBox.about(self,
                          "About me",
                          self.program + " - Custom Serial Program\n\n Version:  v"+ self.version + "\n Written in Python 2.7\n\n (c) Copyright by " + self.author + " 2013 \n All rights reserved. \n\n In Collaboration with \n - Petrovic Darko \n - Gubler Oliver \n\n Visit http://zawiki.dyndns.org\n\n Thanks to\n - Gnome Project - http://art.gnome.org/themes/icon")
    # END Displayinfo
    
    def winCenter(self):
        """ Calculate the Window position in the middle of the screen """
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
    # END win_center
    
# END Class MainUI
