#!/usr/bin/env python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    telims_pipe settings.

"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
import os

#------------------------------------------------------------------------------#
#------------------------------------------------------------------ SETTINGS --#

# root path
root_path = os.path.split(__file__)[0] + '/'

# Window path handling
separator = os.sep
if separator != '/':
    root_path = root_path.replace(os.sep, '/')


# directories
RIG_TOOLS = root_path + 'rig_tools/'
PIPE_UTILS = root_path + 'pipe_utils/'
MODULES = root_path + 'modules/'
IMAGES = root_path + 'images/'
PIPE_UI = root_path + 'pipe_ui/'
CORE = root_path + 'core/'

# sides
sides = ['c', 'l', 'r']

# suffixes
suffixes = [
            "grp", # group
            "jnt", # joint
            "jntEnd", # endJoint
            "loc", # locator
            "geo", # geometry
            "ctrl", # control
            "ikHandle", # ikHandle
            "ikjnt", # ikJoint
            "fkJnt", # fkJoint
            "crv", # curve
            ]

HOOK_NODE_TYPE = 'locator'
META_NODE_TYPE = 'lightInfo'
