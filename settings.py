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

# directories
RIG_TOOLS_PATH = root_path + 'rig_tools/'
AUTORIG_PATH = root_path + 'autorig/'
PIPE_UTILS_PATH = root_path + 'utils/'
MODULES = root_path + 'modules/'
IMAGES = root_path + 'images/'

# sides
sides = ['c', 'l', 'r']

# suffixes
suffixes = [
            "grp", # group
            "jnt", # joint
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
