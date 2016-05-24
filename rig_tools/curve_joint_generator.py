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
import shiboken
import pymel.core as pm
import maya.OpenMayaUI as mui

# 3rd party
from PySide import QtGui, QtCore

# external
import settings
from pipe_utils.name_utils import NameUtils
from pipe_utils.ui_utils import UIUtils

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class CurveJointGenerator(UIUtils):
    """
    Tool for generating joints on a curve.
    """
    def __init__(self, parent=None, gui=True, joints=10, del_curve=True,
                 del_ikHandle=True, asset = "asset", side="l", part="part",
                 suffix="bindJnt", *args, **kwargs):
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

        # super
        super(CurveJointGenerator, self).__init__(parent=parent, *args, **kwargs)

        self.gui = gui
        self.joints = joints
        self.del_curve = del_curve
        self.del_ikHandle = del_ikHandle
        self.asset = asset
        self.side = side
        self.part = part
        self.suffix = suffix

        if self.gui:
            self._build_ui()
        else:
            self._build()

    def _build_ui(self, *kwargs):
        """
        Build UI.
        """
        window_name = "curve_joint_generator"
        window_title = "Curve Joint Generator"
        widget = self.widget()

        # check if window exists
        if pm.window(window_name, exists=True):
            pm.deleteUI(window_name, window=True)

        # create window
        window = self.window(window_name, window_title, widget)

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

        self.asset_name = QtGui.QLineEdit("AssetName")
        self.side = QtGui.QComboBox()
        for side in settings.sides:
            self.side.addItem(side)
        self.part_name = QtGui.QLineEdit("PartOfAsset")
        self.suffix = QtGui.QComboBox()
        for suffix in settings.suffixes:
            if suffix.endswith("Jnt") and suffix != "endJnt":
                self.suffix.addItem(suffix)
        name_layout.addWidget(self.asset_name)
        name_layout.addWidget(self.side)
        name_layout.addWidget(self.part_name)
        name_layout.addWidget(self.suffix)

        # build layout
        build_layout = QtGui.QHBoxLayout()
        layout.addLayout(build_layout)

        build_button = QtGui.QPushButton("Build")
        build_layout.addWidget(build_button)

        # build
        build_button.clicked.connect(self._build)

        # show window
        window.show()

    def _build(self, *args):
        """
        Builds the joints on the curve.
        """
        # naming convention
        asset = self.asset
        side = self.side
        part = self.part
        joints = self.joints
        suffix = self.suffix

        if self.gui:
            asset = self.asset_name.text()
            side = self.side.currentText()
            part = self.part_name.text()
            joints = self.joints_box.value()
            suffix = self.suffix.currentText()
        try:
            curve = pm.ls(sl=True)[0]
            curve_name = NameUtils.get_unique_name(asset, side, part, "crv")
            self.curve = pm.rename(curve, curve_name)
        except IndexError:
            pm.warning("Please select a curve")
            return

        length_of_curve = pm.arclen(self.curve)
        equal_spacing = length_of_curve / float(joints)

        # clear the selection
        pm.select(cl=True)

        # # create the joints
        curve_joints = list()
        for x in xrange(int(joints) + 1):
            name = NameUtils.get_unique_name(asset, side, part, suffix)
            joint = pm.joint(n=name)
            curve_joints.append(joint)

            joint_position = (x * equal_spacing)
            pm.move(0, joint_position, 0)

        # rename last joint
        last_joint = curve_joints[-1]
        pm.rename(last_joint, last_joint + "End")

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
        self._cleanup()


    def _cleanup(self, *args):
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

