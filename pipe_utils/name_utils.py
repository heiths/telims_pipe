#!/usr/bin/env python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    Base module for naming standards.

:use:
    from utils import name_utils
    name = name_utils.get_unique_name(char, side, node_type, suffix)
    loc = pm.spaceLocator(n=name)
"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
from maya import OpenMaya, cmds

# external
import settings

#------------------------------------------------------------------------------#
#----------------------------------------------------------------- FUNCTIONS --#

class NameUtils(object):
    """
    Base Class for naming convetions.
    """
    def __init__(self, **kwargs):
        """
        The initializer
        """
        pass

    @classmethod
    def get_unique_name(self, asset = "asset", side = "c",  part = "part",
                        suffix = "loc", security = 50):
        """
        Builds unique name based off the following parameters.

        :parameters:
            asset: Name of the asset, i.e., Batman, car, cheetah.
            side: Right, Left, or Center (r, l, c).
            part: The part of the asset, i.e., arm, door, tail.
            suffix: The name of the object, i.e., loc, jnt, geo.
            security: The number of parts that can be named.

        :NOTE:
            Security is set to 50 by default and does not need to be set unless
            a higher about of parts are needed.
        """

        # naming convention
        root_name = '{0}_{1}_{2}0{3}_{4}'
        name = root_name.format(asset, side, part, str(1), suffix)

        count = 1
        if not side in settings.sides:
            OpenMaya.MGlobal.displayError("Side is not valid")
            return
        if not suffix in settings.suffixes:
            OpenMaya.MGlobal.displayError("Suffix is not valid")
            return

        while cmds.objExists(name) == 1:
            if count < security:
                count += 1
                name = root_name.format(asset, side, part, count, suffix)
            else:
                OpenMaya.MGlobal.displayWarning("Please increase security level")
                break
        return name
