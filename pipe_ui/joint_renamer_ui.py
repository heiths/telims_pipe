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

# 3rd party
from maya import cmds, mel
import maya.OpenMayaUI as mui
from PySide import QtGui, QtCore

# external
import settings
from rig_tools import joint_renamer
from pipe_utils.ui_utils import UIUtils

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class JointRenamer(UIUtils):
    """
    Tool for renaming joints.
    """
    def __init__(self, parent=None, *args, **kwargs):

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
        window_title = "Joint Renamer"
        widget = self.widget()

        # check if window exists
        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name, window=True)

        # create window
        window = self.window(window_name, window_title, widget)
        window.setWindowFlags(QtCore.Qt.Window)
        window.setMinimumSize(350, 320)
        window.setMaximumSize(350, 320)

        # main layout
        layout = QtGui.QVBoxLayout(widget)

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
        self.selected_joints.setChecked(True)
        self.end_joint = QtGui.QCheckBox("End Joint")

        options_layout.addWidget(self.selected_joints)
        options_layout.addWidget(self.end_joint)

        # tools
        UIUtils.qt_divider_label(options_layout, "Tools")
        tools_layout = QtGui.QVBoxLayout()
        tools_layout.setAlignment(QtCore.Qt.AlignBottom)
        options_layout.addLayout(tools_layout)

        toggle_local_axis_button = QtGui.QPushButton("Toggle Local Axis")
        joint_orient_tool_button = QtGui.QPushButton("Joint Orient Tool")
        freeze_transforms_button = QtGui.QPushButton("Freeze Transforms")

        freeze_transforms_box_layout = QtGui.QHBoxLayout()
        self.translation_box = QtGui.QCheckBox("T")
        self.rotation_box = QtGui.QCheckBox("R")
        self.scale_box = QtGui.QCheckBox("S")
        boxes = (self.translation_box, self.rotation_box, self.scale_box)
        for box in boxes:
            box.setChecked(True)
        freeze_transforms_box_layout.addWidget(self.translation_box)
        freeze_transforms_box_layout.addWidget(self.rotation_box)
        freeze_transforms_box_layout.addWidget(self.scale_box)

        tools_layout.addWidget(toggle_local_axis_button)
        tools_layout.addWidget(joint_orient_tool_button)
        tools_layout.addWidget(freeze_transforms_button)
        tools_layout.addLayout(freeze_transforms_box_layout)

        # joint list
        joint_list_layout = QtGui.QVBoxLayout()
        settings_layout.addLayout(joint_list_layout)

        self.joint_list = QtGui.QListWidget()
        multiple_selection = QtGui.QAbstractItemView.ExtendedSelection
        self.joint_list.setSelectionMode(multiple_selection)
        self.joint_list.setMaximumWidth(200)
        joint_list_layout.addWidget(self.joint_list)

        # populate
        self._refresh_joint_list()

        # build layout
        build_layout = QtGui.QHBoxLayout()
        layout.addLayout(build_layout)

        rename_button = QtGui.QPushButton("Rename")
        build_layout.addWidget(rename_button)

        # on enter
        rename_button.setAutoDefault(True)
        self.part_name.returnPressed.connect(rename_button.click)
        self.asset_name.returnPressed.connect(rename_button.click)

        # signals
        rename_button.clicked.connect(self._rename)
        toggle_local_axis_button.clicked.connect(self._toggle_local_axis)
        joint_orient_tool_button.clicked.connect(self._joint_orient_tool)
        freeze_transforms_button.clicked.connect(self._freeze_transforms)
        self.selected_joints.stateChanged.connect(self._selection_mode)
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

    def _toggle_local_axis(self):
        """
        Toggles the local axis of selected joints.
        """
        cmds.toggle(la=True)

    def _joint_orient_tool(self):
        """
        Loads Maya's joint orient tool.
        """
        mel.eval("OrientJointOptions;")

    def _freeze_transforms(self):
        """
        Freezes transforms on joints.
        """
        t = self.translation_box.isChecked()
        r = self.rotation_box.isChecked()
        s = self.scale_box.isChecked()

        selection = cmds.ls(sl=True, type="joint")
        if not selection:
            return cmds.warning("No Joints selected")
        cmds.makeIdentity(selection, a=True, t=t, r=r, s=s)

    def _refresh_joint_list(self):
        """
        Refreshes the joint_list widget.
        """
        joints = cmds.ls(type="joint")
        UIUtils.qt_list_widget_add_items(self.joint_list, joints, True)

    def _selection_mode(self):
        """
        Changes the state of selection in joint_list.
        """
        multiple_selection = QtGui.QAbstractItemView.ExtendedSelection
        if not self.selected_joints.isChecked():
            multiple_selection = QtGui.QAbstractItemView.SingleSelection
        self.joint_list.setSelectionMode(multiple_selection)
