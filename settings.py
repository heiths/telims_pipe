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
MODULES = root_path + 'modules/'
IMAGES = root_path + 'images/'
PIPE_UI = root_path + 'pipe_ui/'
PIPE_CORE = root_path + 'pipe_core/'
PIPE_UTILS = root_path + 'pipe_utils/'
MEL = root_path + "mel/"
ICON_PATH = IMAGES + "icons/"
THIRD_PARTY = root_path + "third_party/"

# dir tuple
directories = (RIG_TOOLS, PIPE_UTILS, MODULES, IMAGES, PIPE_UI, PIPE_CORE,
               MEL, ICON_PATH)

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
