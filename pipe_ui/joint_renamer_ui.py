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
        window.setMinimumSize(350, 200)
        window.setMaximumWidth(200)
        window.setObjectName(window_name)
        window.setWindowFlags(QtCore.Qt.Window)
        window.setWindowTitle("Joint Renamer")

        # main layout
        layout = QtGui.QVBoxLayout(self.main_widget)

        # basic name convention label
        UIUtils.qt_divider_label(layout, "Naming Convention")

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

        # settings label
        UIUtils.qt_divider_label(layout, "settings")

        # settings
        settings_layout = QtGui.QHBoxLayout()
        layout.addLayout(settings_layout)

        # options
        options_layout = QtGui.QVBoxLayout()
        options_layout.setAlignment(QtCore.Qt.AlignTop)
        settings_layout.addLayout(options_layout)

        self.selected_joints = QtGui.QCheckBox("Selected Joints")
        self.end_joint = QtGui.QCheckBox("End Joint")
        options_layout.addWidget(self.selected_joints)
        options_layout.addWidget(self.end_joint)

        # joint list
        joint_list_layout = QtGui.QVBoxLayout()
        settings_layout.addLayout(joint_list_layout)

        self.joint_list = QtGui.QListWidget()
        multiple_selection = QtGui.QAbstractItemView.ExtendedSelection
        self.joint_list.setSelectionMode(multiple_selection)
        self.joint_list.setMaximumWidth(170)
        joint_list_layout.addWidget(self.joint_list)

        # populate
        self._refresh_joint_list()

        # build layout
        build_layout = QtGui.QHBoxLayout()
        layout.addLayout(build_layout)

        build_button = QtGui.QPushButton("Rename")
        build_button.setDefault(True)
        build_layout.addWidget(build_button)

        # signals
        build_button.clicked.connect(self._rename)
        self.joint_list.itemClicked.connect(self._select_joints)

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
        selected_joints = self.selected_joints.isChecked()
        end_joint = self.end_joint.isChecked()

        # build
        self.renamer_obj.rename(asset, side, part, suffix,
                                selected_joints, end_joint)
        self._refresh_joint_list()

    def _select_joints(self, *args):
        """
        Selects joints based on selection from joint_list.
        """
        selected_joints = list()
        joint_list = self.joint_list.selectedItems()
        selection = cmds.ls(sl=True)

        # select items
        for joint in joint_list:
            cmds.select(joint.text(), add=True)
            selected_joints.append(joint.text())

        # deselect items not in the active list
        for joint in selection:
            if joint not in selected_joints:
                cmds.select(joint, d=True)

    def _refresh_joint_list(self):
        """
        Refreshes the joint_list widget.
        """
        joints = cmds.ls(type="joint")
        UIUtils.qt_list_widget_add_items(self.joint_list, joints, True)
