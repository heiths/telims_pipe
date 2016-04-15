#!/usr/bin/python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    Rig Tools
"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in

# third party
import pymel.core as pm
from maya import cmds, mel

# external
from pipe_utils.name_utils import NameUtils

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class RigTools(object):
    """
    Rig Tools, for simple rig solutions.
    """
    def __init__(self, *args, **kwargs):
        """
        The initializer.
        """

    @classmethod
    def build_forearm_twist(self, elbow_joint=None, hand_joint=None, *args):
       """
       Builds twist joints for a forearm twist.
       @ARGS:
           asset, side, part, suffix (see pipe_utils.name_utils.NameUtils)
       NOTES:
           Build with or without args.
           args = ("fortniteSmasher", "r", "arm", "twistJnt")
           tools.RigTools.build_forearm_twist("lowerarm_r", "hand_r", *args)
       """
       # if args
       if not args:
           args = ("asset", "ud", "limb", "twistJnt")

       # grab necissary joints
       if not elbow_joint and hand_joint:
           selection = cmds.ls(sl=True)
           elbow_joint = selection[0]
           hand_joint = selection[1]

       # get values
       joint_distance_value = cmds.getAttr("{0}.tx".format(hand_joint))
       split_tuple = (.25, .5, .75)

       # build joints
       twist_joints = list()
       for value in split_tuple:
           twist_joint_name = NameUtils.get_unique_name(*args)
           temp_joint = cmds.duplicate(elbow_joint, rr=True)[0]
           twist_joint = cmds.rename(temp_joint, twist_joint_name)
           cmds.delete(cmds.listRelatives(twist_joint, f=True, ad=True, c=True))
           cmds.parent(twist_joint, elbow_joint)
           position = joint_distance_value * value
           cmds.setAttr("{0}.tx".format(twist_joint), position)
           twist_joints.append(twist_joint)

       # apply orient contraints
       for count, joint in enumerate(twist_joints):
           if count > 1:
               break
           contraint = cmds.orientConstraint(elbow_joint, twist_joints[-1],
                                             twist_joints[count])[0]
           if count == 0:
               cmds.setAttr("{0}.{1}W0".format(contraint, elbow_joint), 2)
           elif count == 1:
               cmds.setAttr("{0}.{1}W1".format(contraint, twist_joints[-1]), 2)

       # TODO: apply aim contraint using aim axis

    @classmethod
    def build_stretchy_limb(self):
        """
        Builds a stretchy rig for an IK/FK/Bind joint limb setup.
        """
        pass

    @classmethod
    def hide_show_joints(self):
        """
        Hides and shows joints.
        """
        # clear selection
        cmds.select(cl=True)

        # query for joints
        active_view = pm.getPanel(withFocus=True)
        try:
            joints = pm.modelEditor(active_view, q=True, joints=True)
        except RuntimeError:
            cmds.warning("Please make sure you're in an active view port.")
            return

        # set display mode
        if joints:
            pm.modelEditor(active_view, e=True, joints=False)
        else:
            pm.modelEditor(active_view, e=True, joints=True)



