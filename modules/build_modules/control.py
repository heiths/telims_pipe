#!/usr/bin/env python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    Base class for creating controls.

:use:
    from base import control
    ctrl_class = control.Control(asset, side, part, size, color)
    ctrl_class.circle_cc()

"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
import pymel.core as pm

# external
from utils.name_utils import NameUtils
from utils import xform_utils

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class Control(object):
    """
    Base control class.
    """
    def __init__(self, asset='asset', side='c', part='part',
                 size=1, color='yellow', aim_axis='x', security=50):
        """
        The constructor.
        """
        # naming convention
        self.asset = asset
        self.side = side
        self.part = part
        self.security = security

        # settings
        self.color = color
        self.size = size
        self.aim_axis = aim_axis

        self.ctrl = None
        self.ctrl_grp = None
        self.ctrl_name = None

    def circle_ctrl(self):
        """
        Builds a circle control.
        """
        self._build_name()
        if self.ctrl_name:
            self.ctrl = pm.circle(n=self.ctrl_name, ch=0, o=1, nr=[1, 0, 0])[0]

        self._finalize_ctrl()

    def _build_name(self):
        """
        Builds the name of the control.
        """
        self.ctrl_name = NameUtils.get_unique_name(self.asset,
                                                   self.side,
                                                   self.part,
                                                   "ctrl",
                                                   self.security)

    def _finalize_ctrl(self):
        """
        Orientates, scales and zeroes out the control.
        """
        self._aim_ctrl()
        self._set_ctrl_color()

        if self.size != 1:
            for shape in self.ctrl.getShapes():
                pm.scale(shape.cv, self.size, self.size, self.size, r=1)
            pm.delete(self.ctrl, ch=1)

        self.ctrl_grp = xform_utils.zero(self.ctrl)

    def _aim_ctrl(self):
        """
        Aims control based on a provided aim axis.
        """
        y = 0
        z = 0

        if self.aim_axis == "y":
            z = 90
        elif self.aim_axis == "z":
            y = -90

        for shape in self.ctrl.getShapes():
            pm.rotate(shape.cv, 0, y, z, r=1)

    def _set_ctrl_color(self):
        """
        Sets the color of the control object.
        """
        for shape in self.ctrl.getShapes():
            if self.color == "yellow":
                shape.overrideEnabled.set(True)
                shape.overrideColor.set(17)
            elif self.color == "blue":
                if self.side == "l":
                    shape.overrideEnabled.set(True)
                    shape.overrideColor.set(6)
                elif self.side == "r":
                    shape.overrideEnabled.set(True)
                    shape.overrideColor.set(13)
            elif self.color == "red":
                if self.side == "l":
                    shape.overrideEnabled.set(True)
                    shape.overrideColor.set(13)
                elif self.side == "r":
                    shape.overrideEnabled.set(True)
                    shape.overrideColor.set(6)
