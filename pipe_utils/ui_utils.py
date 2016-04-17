#!/usr/bin/env python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    Base class for UI constructors.
"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
import shiboken
import maya.OpenMayaUI as mui

# 3rd party
from PySide import QtGui, QtCore

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class UIUtils(object):
    """
    Base class for UI constructors.
    """
    def __init__(self):
        """
        The constructor.
        """
        pass

    @classmethod
    def get_maya_window(self):
        """
        Grabs the Maya window.
        """
        pointer = mui.MQtUtil.mainWindow()
        return shiboken.wrapInstance(long(pointer), QtGui.QWidget)
