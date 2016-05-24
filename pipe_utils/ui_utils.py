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
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class UIUtils(MayaQWidgetBaseMixin, QtGui.QWidget):
    """Base class for UI constructors."""

    save_button = QtGui.QMessageBox.Yes

    def window(self, wname=None, wtitle=None, cwidget=None):
        """Defines basic window parameters."""
        parent = self.get_maya_window()
        window = QtGui.QMainWindow(parent)

        if wname:
            window.setObjectName(wname)
        if wtitle:
            window.setWindowTitle(wtitle)
        if cwidget:
            window.setCentralWidget(cwidget)
        return window

    def get_maya_window(self):
        """Grabs the Maya window."""
        pointer = mui.MQtUtil.mainWindow()
        return shiboken.wrapInstance(long(pointer), QtGui.QWidget)

    def widget(self):
        """Main Widget"""
        return QtGui.QWidget()

    def qt_divider_label(self, layout, label):
        """Creates a centered label header."""
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

    def qt_list_widget_add_items(self, widget, items, clear=None):
        """Qt Wrapper for QListWidget for adding items."""
        if clear:
            self.clear_widget(widget)

        for item_text in items:
            item = QtGui.QListWidgetItem(item_text)
            widget.addItem(item)

    def clear_widget(self, widget):
        """Clears items in a widget."""
        widget.clear()

    def warning(self, message, button_one=None, button_two=None):
        """Method for prompting the user with a warning."""
        if not button_one:
            button_one = QtGui.QMessageBox.Ok
        if not button_two:
            button_two = QtGui.QMessageBox.Cancel
        args = [self, "Warning", message, button_one, button_two]
        warning = QtGui.QMessageBox.warning(*args)
        return warning


