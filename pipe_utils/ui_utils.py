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

    @classmethod
    def get_maya_window(cls):
        """
        Grabs the Maya window.
        """
        pointer = mui.MQtUtil.mainWindow()
        return shiboken.wrapInstance(long(pointer), QtGui.QWidget)

    @classmethod
    def qt_divider_label(cls, layout, label):
        """
        Creates a centered label header.
        """
        # attach to layout
        divider_layout = QtGui.QHBoxLayout()
        layout.addLayout(divider_layout)

        # define divider
        divider_label = QtGui.QLabel(label)
        divider_label.setAlignment(QtCore.Qt.AlignCenter)
        divider_label.setMinimumHeight(20)
        divider_left = QtGui.QFrame()
        divider_left.setFrameShape(QtGui.QFrame.HLine)
        divider_left.setFrameShadow(QtGui.QFrame.Sunken)
        divider_right = QtGui.QFrame()
        divider_right.setFrameShape(QtGui.QFrame.HLine)
        divider_right.setFrameShadow(QtGui.QFrame.Sunken)
        divider_layout.addWidget(divider_left)
        divider_layout.addWidget(divider_label)
        divider_layout.addWidget(divider_right)

    @classmethod
    def qt_list_widget_add_items(cls, widget, items, clear=None):
        """
        Qt Wrapper for QListWidget for adding items.
        """
        if clear:
            cls._clear_widget(widget)

        for item_text in items:
            item = QtGui.QListWidgetItem(item_text)
            widget.addItem(item)

    @classmethod
    def _clear_widget(cls, widget):
        """
        Clears items in a widget.
        """
        widget.clear()


