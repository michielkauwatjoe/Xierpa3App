# -*- coding: UTF-8 -*-
# -----------------------------------------------------------------------------
#    xierpa server
#    Copyright (c) 2014+  buro@petr.com, www.petr.com, www.xierpa.com
#
#    X I E R P A  3  A P P
#    Distribution by the MIT License.
#
# -----------------------------------------------------------------------------
#
#    python setup.py py2app
#
"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

setup(
    app=['main.py'],
    name="Xierpa3",
    data_files=['en.lproj', ],
    setup_requires=['py2app'],
    options=dict(py2app=dict(includes=['lxml.etree', 'lxml._elementpath',], packages=['xierpa3']))
)
