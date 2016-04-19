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

# build in
from random import randint

# third-party
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

    def rename(self, asset, side, part, suffix, selected=None, end_joint=None):
        """
        Renames joint hierarchy.
        """
        new_joints = list()
        tmp_joints = list()

        # get joints
        joint_chain = cmds.ls(sl=True, dag=True, sn=True, type="joint")
        if selected:
            joint_chain = cmds.ls(sl=True, type="joint")

        # check for selection
        if not joint_chain:
            return cmds.warning("No Joints selected")

        # for rebuilding
        for joint in joint_chain:
            random = randint(10000, 99999)
            tmp_name = joint + str(random)
            tmp_joint = cmds.rename(joint, tmp_name)
            tmp_joints.append(tmp_joint)

        # rename
        for joint in tmp_joints:
            new_name = NameUtils.get_unique_name(asset, side, part, suffix)
            if cmds.objExists(joint):
                new_joint = cmds.rename(joint, new_name)
                new_joints.append(new_joint)

        # end joint
        if end_joint:
            last_joint = new_joints[-1]
            last_joint = cmds.rename(last_joint, last_joint + "End")
