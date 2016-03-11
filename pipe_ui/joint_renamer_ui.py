#!/usr/bin/env python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    Tool for renaming joints.
"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
import shiboken
from maya import cmds
import maya.OpenMayaUI as mui

# 3rd party
from PySide import QtGui, QtCore

# external
import settings
from rig_tools import joint_renamer
from pipe_utils.ui_utils import UIUtils

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class JointRenamer(QtGui.QDialog):
    """
    Tool for renaming joints.
    """
    def __init__(self, *args, **kwargs):
        """
        Defines the joint renamer tool.

        :parameters:
            asset: For naming convention.
            side: For naming convention. (r, l, c)
            part: For naming convention.
        """
        # grab api class
        self.renamer_obj = joint_renamer.JointRenamer()


        self.asset = None
        self.side = None
        self.part = None

        self.build_ui()


    def build_ui(self, *kwargs):
        """
        Build gui
        """
        window_name = "joint_renamer"

        # check if window exists
        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name, window=True)

        # create window
        parent = UIUtils.get_maya_window()
        window = QtGui.QMainWindow(parent)
        window.setMinimumSize(300, 80)
        window.setMaximumSize(300, 80)
        window.setObjectName(window_name)
        window.setWindowTitle("Joint Renamer")

        # central widget
        widget = QtGui.QWidget()
        window.setCentralWidget(widget)

        # main layout
        layout = QtGui.QVBoxLayout(widget)

        # naming convention
        name_layout = QtGui.QHBoxLayout()
        layout.addLayout(name_layout)

        self.asset_name = QtGui.QLineEdit("AssetName")
        self.side = QtGui.QComboBox()
        for side in settings.sides:
            self.side.addItem(side)
        self.part_name = QtGui.QLineEdit("PartOfAsset")
        name_layout.addWidget(self.asset_name)
        name_layout.addWidget(self.side)
        name_layout.addWidget(self.part_name)

        # build layout
        build_layout = QtGui.QHBoxLayout()
        layout.addLayout(build_layout)

        build_button = QtGui.QPushButton("Rename")
        build_button.setDefault(True)
        build_layout.addWidget(build_button)

        # build
        build_button.clicked.connect(self._rename)

        # show window
        window.show()

    def _rename(self, *args):
        """
        Renames joint hierarchy.
        """
        # naming convention
        asset = self.asset_name.text()
        side = self.side.currentText()
        part = self.part_name.text()

        # build
        self.renamer_obj.rename(asset, side, part)

