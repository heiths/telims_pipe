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

# build int
from maya import cmds

# external
from pipe_utils.name_utils import NameUtils

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class JointRenamer(object):
    """
    Tool for renaming joints.
    """
    def __init__(self):
        """
        Defines the joint renamer tool.
        """
        pass

    def rename(self, asset, side, part, suffix):
        """
        Renames joint hierarchy.
        """
        # get joints
        joint_chain = cmds.ls(sl=True, dag=True, sn=True, type="joint")

        # check for selection
        if not joint_chain:
            return cmds.warning("No Joints selected")

        # rename
        for joint in joint_chain:
            new_name = NameUtils.get_unique_name(asset, side, part, suffix)
            if joint == joint_chain[-1]:
                cmds.rename(joint, new_name + "End")
                continue
            cmds.rename(joint, new_name)
