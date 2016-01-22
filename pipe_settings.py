#!/usr/bin/env python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    Rig standards.

:use:

long description

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
PIPE_UTILS_PATH = root_path + 'pipe_utils/'

# sides
sides = ['c', 'l', 'r']

# suffixes
suffixes = [
            "grp", # group
            "jnt", # joints
            "loc", # locators
            "geo", # geometry
            "ctrl", # controls
            "ikHandle", # ikHandle
            "ikjnt", # ikJoint
            "fkjnt", # fkJoint
            ]
