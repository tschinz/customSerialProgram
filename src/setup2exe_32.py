#!/usr/bin/env python
# filename:          setup2exe.py
# kind:              Python file
# first created:     30.08.2012
# created by:        zas
#
################################################################################
# History:
#
# v0.1 : zas 30.08.2012
#
################################################################################
# Description: 
# script to generate a Windows executable (no Python required afterwards)
################################################################################
# Installation: 
# Module     : py2exe
# Win only   : py2exe installer, Microsoft Visual C++ 2008 Redistributable Package
# DLL needed : Python26/DLLs/msvcp90.dll 
################################################################################
__author__ = "Zahno Silvan"
__date__   = "30.08.2012"

################################################################################
# Import modules
#
from distutils.core import setup
import py2exe, sys, os
import shutil

################################################################################
# Constants
#
includes = ['sip']
excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger',
            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
            'Tkconstants', 'Tkinter']
packages = []
dll_excludes = ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll', 'tcl84.dll',
                'tk84.dll']

################################################################################
# Py2exe setup
#
sys.argv.append('py2exe')

setup(
    name = 'CSP',
    version = '1.7',
    description = 'CustonSerialProgram',
    author = 'Zahno Silvan',
    options = {"py2exe": {"compressed": 2,
                          "optimize": 0,
                          "includes": includes,
                          "excludes": excludes,
                          "packages": packages,
                          "dll_excludes": dll_excludes,
                          "bundle_files": 3,
                          "dist_dir": "bin",
                          "xref": False,
                          "skip_archive": False,
                          "ascii": False,
                          "custom_boot_script": '',
                         }
              },
    windows = [{ "script": 'csp.pyw',
                 "icon_resources" : [(0, "icons/logo.ico")]
              }],
    
    data_files=[("icons",
                 ["icons/add.png", 
                  "icons/close.png",
                  "icons/clean.png",
                  "icons/exit.png",
                  "icons/help.png",
                  "icons/info.png",
                  "icons/logo.png",
                  "icons/logo.ico",
                  "icons/min.png",
                  "icons/open.png",
                  "icons/record.png",
                  "icons/recording.png",
                  "icons/reset.png",
                  "icons/send.png",
                  "icons/zas.png",]),
                ("commands.cmd"),
                ("settings.ini")]
    )

print("Remove old bin32")
end_loc = "./../bin32"
bin_loc = "./bin"
build_loc = "./build"
if os.path.exists(end_loc):
    shutil.rmtree(end_loc)
print("Copy new bin32")
shutil.copytree(bin_loc, end_loc)
print("Remove intermediate folders")
shutil.rmtree(bin_loc)
shutil.rmtree(build_loc)

print("Py2Exe finished")


