#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    abc_pipe settings.
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
COMET_TOOLS = root_path + "comet_tools/"

# dir tuple
directories = (RIG_TOOLS, PIPE_UTILS, MODULES, IMAGES, PIPE_UI, CORE,
               COMET_TOOLS,)

# sides
sides = ['c', 'l', 'r']

# suffixes
suffixes = [
            "grp", # group
            "bindJnt", # bindJnt
            "loc", # locator
            "geo", # geometry
            "ctrl", # control
            "ikHandle", # ikHandle
            "ikJnt", # ikJnt
            "fkJnt", # fkJnt
            "crv", # curve
            ]

HOOK_NODE_TYPE = 'locator'
META_NODE_TYPE = 'network'
