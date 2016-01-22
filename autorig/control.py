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
    ctrl_class = control.Control(char, side, node_type, size, color)
    ctrl_class.circle_cc()

"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
import pymel.core as pm

# external
from utils import xform_utils, name_utils

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class Control(object):
    """
    Base control class.
    """
    def __init__(self, char='char', side='c', node_type='default',
                 size=1, color='yellow', aim_axis='x'):
        """
        The constructor.
        """
        # naming convention
        self.char = char
        self.side = side
        self.node_type = node_type

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
        self.ctrl_name = name_utils.get_unique_name(self.char,
                                                    self.side,
                                                    self.node_type,
                                                    "ctrl")

    def _finalize_ctrl(self):
        """
        Orientates, scales and zeroes out the control.
        """
        self._aim_ctrl()
        self._color_ctrl()

        if self.size != 1:
            for s in self.ctrl.getShapes():
                pm.scale(s.cv, self.size, self.size, self.size, r=1)
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

        for s in self.ctrl.getShapes():
            pm.rotate(s.cv, 0, y, z, r=1)

    def set_ctrl_color(self):
        """
        Sets the color of the control object.
        """
        for s in self.ctrl.getShapes():
            pm.rotate(s.cv, 0, y, z, r = 1)
            if self.ctrl_color == "yellow":
                s.overrideEnabled.set(True)
                s.overrideColor.set(17)
            elif self.ctrl_color == "blue":
                if self.side == "l":
                    s.overrideEnabled.set(True)
                    s.overrideColor.set(6)
                elif self.side == "r":
                    s.overrideEnabled.set(True)
                    s.overrideColor.set(13)
            elif self.cc_color == "red":
                if self.side == "l":
                    s.overrideEnabled.set(True)
                    s.overrideColor.set(13)
                elif self.side == "r":
                    s.overrideEnabled.set(True)
                    s.overrideColor.set(6)
