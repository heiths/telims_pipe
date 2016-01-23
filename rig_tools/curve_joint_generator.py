#!/usr/bin/env python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    For building joints along a curve.
"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
import pymel.core as pm
import maya.OpenMayaUI as mui
import shiboken

# 3rd party
from PySide import QtGui, QtCore

# external
from utils.name_utils import NameUtils
import settings

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class CurveJointGenerator(QtGui.QDialog):
    """
    Tool for generating joints on a curve.
    """
    def __init__(self, gui=True, joints=10, del_curve=True, del_ikHandle=True,
                 asset = "asset", side="l", part="part"):
        """
        Defines the curve joint generator.

        :parameters:
            gui: Gui option, if false, it'll run the tool with 10 joints.
            joints: How many joints you want along the curve.
            del_curve: Whether or not you want to delete the curve.
            del_ikHandle: Whether or not you want to delete the ikHandle.
            asset: For naming convention.
            side: For naming convention. (r, l, c)
            part: For naming convention.

        """

        self.gui = gui
        self.joints = joints
        self.del_curve = del_curve
        self.del_ikHandle = del_ikHandle
        self.asset = asset
        self.side = side
        self.part = part

        if self.gui:
            self.build_gui()
        else:
            self.build()

    def build_gui(self, *kwargs):
        """
        Build gui
        """
        window_name = "curve_joint_generator"

        # check if window exists
        if pm.window("curve_joint_generator", exists=True):
            pm.deleteUI("curve_joint_generator", window=True)

        # create window
        parent = self.get_maya_window()
        window = QtGui.QMainWindow(parent)
        window.setObjectName(window_name)
        window.setWindowTitle("Curve Joint Generator")

        # central widget
        widget = QtGui.QWidget()
        window.setCentralWidget(widget)

        # main layout
        layout = QtGui.QVBoxLayout(widget)

        # tool settings
        joints_layout = QtGui.QHBoxLayout()
        layout.addLayout(joints_layout)

        text = QtGui.QLabel("Number of Joints")
        self.joints_box = QtGui.QSpinBox()
        self.joints_box.setMinimum(1)
        self.del_curve = QtGui.QCheckBox()
        self.del_curve.setText("Curve")
        self.del_ikHandle = QtGui.QCheckBox()
        self.del_ikHandle.setText("ikHandle")
        joints_layout.addWidget(text)
        joints_layout.addWidget(self.joints_box)
        joints_layout.addWidget(self.del_curve)
        joints_layout.addWidget(self.del_ikHandle)

        # divider
        spacer = QtGui.QSpacerItem(40, 10, QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Minimum)
        layout.addItem(spacer)

        # naming convention
        name_layout = QtGui.QHBoxLayout()
        layout.addLayout(name_layout)

        self.asset_name = QtGui.QLineEdit("Asset Name")
        self.side = QtGui.QComboBox()
        for side in settings.sides:
            self.side.addItem(side)
        self.part_name = QtGui.QLineEdit("Part of Asset")
        name_layout.addWidget(self.asset_name)
        name_layout.addWidget(self.side)
        name_layout.addWidget(self.part_name)

        # build layout
        build_layout = QtGui.QHBoxLayout()
        layout.addLayout(build_layout)

        build_button = QtGui.QPushButton("Build")
        build_layout.addWidget(build_button)

        # build
        build_button.clicked.connect(self.build)

        # show window
        window.show()

    def get_maya_window(self):
        """
        Grabs the Maya window.
        """
        pointer = mui.MQtUtil.mainWindow()
        return shiboken.wrapInstance(long(pointer), QtGui.QWidget)

    def build(self, *args):
        """
        Builds the joints on the curve.
        """
        # naming convention
        asset = self.asset
        side = self.side
        part = self.part
        joints = self.joints
        security = joints + 1

        if self.gui:
            asset = self.asset_name.text()
            side = self.side.currentText()
            part = self.part_name.text()
            joints = self.joints_box.value()
            print joints
            security = joints + 1
        try:
            self.curve = pm.ls(sl=True)[0]
            curve_name = NameUtils.get_unique_name(asset, side, part, "crv")
            pm.rename(self.curve, curve_name)
        except IndexError:
            pm.warning("Please select a curve")
            return

        length_of_curve = pm.arclen(self.curve)
        equal_spacing = length_of_curve / float(joints)

        # clear the selection
        pm.select(cl=True)

        # # create the joints
        for x in xrange(int(joints) + 1):
            name = NameUtils.get_unique_name(asset, side, part, "jnt", security)
            pm.joint(n=name)

            joint_position = (x * equal_spacing)
            pm.move(0, joint_position, 0)

        root_joint = pm.selected()[0].root()
        end_joint = pm.ls(sl=True)[0]
        solver = 'ikSplineSolver'

        # attach joints to curve
        ik_name = NameUtils.get_unique_name(asset, side, part, "ikHandle")
        self.ikHandle = pm.ikHandle(sj=root_joint, ee=end_joint, sol=solver,
                        c=self.curve, pcv=True, roc=True, ccv=False, n=ik_name)
        joint_chain = pm.ls(root_joint, dag=True)

        # delete history
        pm.makeIdentity(root_joint, apply=True)

        # cleanup
        self.cleanup()


    def cleanup(self, *args):
        """
        Cleanup
        """
        pm.select(cl=True)
        del_curve = self.del_curve
        del_ikHandle = self.del_ikHandle

        # delete curve and ikHandle
        if self.gui:
            del_curve = self.del_curve.checkState()
            del_ikHandle = self.del_ikHandle.checkState()
        if not del_curve:
            pm.delete(self.curve)
        if not del_ikHandle:
            pm.delete(self.ikHandle)

