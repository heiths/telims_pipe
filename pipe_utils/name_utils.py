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

#------------------------------------------------------------------------------#
#----------------------------------------------------------------- FUNCTIONS --#

class NameUtils(object):
    """
    Base Class for naming convetions.
    """
    def __init__(self, *args, **kwargs):
        """
        The initializer
        """
        pass

    @classmethod
    def get_unique_name(self, asset="asset", side="c", part="part", suffix="loc"):
        """
        Builds unique name based off the following parameters.

        :parameters:
            asset: Name of the asset, i.e., Batman, car, cheetah.
            side: Right, Left, or Center (r, l, c).
            part: The part of the asset, i.e., arm, door, tail.
            suffix: The name of the object, i.e., loc, jnt, geo.
        """

        # naming convention
        root_name = '{0}_{1}_{2}0{3}_{4}'
        name = root_name.format(asset, side, part, str(1), suffix)

        count = 1
        while cmds.objExists(name):
            count += 1
            name = root_name.format(asset, side, part, count, suffix)

        return name
