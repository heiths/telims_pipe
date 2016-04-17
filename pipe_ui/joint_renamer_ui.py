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
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

# external
import settings
from rig_tools import joint_renamer
from pipe_utils.ui_utils import UIUtils

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class JointRenamer(MayaQWidgetBaseMixin, QtGui.QWidget):
    """
    Tool for renaming joints.
    """
    def __init__(self, parent=None, *args, **kwargs):
        """
        Defines the joint renamer tool.

        :parameters:
            asset: For naming convention.
            side: For naming convention. (r, l, c)
            part: For naming convention.
        """
        # super and api class
        super(JointRenamer, self).__init__(parent=parent, *args, **kwargs)
        self.renamer_obj = joint_renamer.JointRenamer()

        self.asset = None
        self.side = None
        self.part = None
        self.suffix = None

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
        self.main_widget = QtGui.QWidget()
        window.setCentralWidget(self.main_widget)
        window.setMinimumSize(350, 80)
        window.setMaximumSize(350, 80)
        window.setObjectName(window_name)
        window.setWindowFlags(QtCore.Qt.Window)
        window.setWindowTitle("Joint Renamer")

        # main layout
        layout = QtGui.QVBoxLayout(self.main_widget)

        # naming convention
        name_layout = QtGui.QHBoxLayout()
        layout.addLayout(name_layout)

        self.asset_name = QtGui.QLineEdit("AssetName")
        self.side = QtGui.QComboBox()
        for side in settings.sides:
            self.side.addItem(side)
        self.part_name = QtGui.QLineEdit("PartOfAsset")

        self.suffix = QtGui.QComboBox()
        for suffix in settings.suffixes:
            if suffix.endswith("Jnt"):
                self.suffix.addItem(suffix)
        name_layout.addWidget(self.asset_name)
        name_layout.addWidget(self.side)
        name_layout.addWidget(self.part_name)
        name_layout.addWidget(self.suffix)

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
        suffix = self.suffix.currentText()

        # build
        self.renamer_obj.rename(asset, side, part, suffix)

