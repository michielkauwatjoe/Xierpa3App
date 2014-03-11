# -*- coding: UTF-8 -*-
#
#    X I E R P A   3
#    OS X Application (c) 2014 buro@petr.com, www.petr.com, www.xierpa.com
#    Authors: Petr van Blokland, Michiel Kauw���A���Tjoe
#
#    No distribution without permission.
#
#    python setup.py py2app
#

"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""
from setuptools import setup

APP = ['Xierpa3App.py']
DATA_FILES = ['Resources/English.lproj', ]
OPTIONS = {'argv_emulation': True,
           'iconfile': 'images/icon.icns'}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)