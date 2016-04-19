#!/usr/bin/env python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    Base __init__ for telims_pipe

:use:
    Instead of reloading individual modules simply reload(telims_pipe)
    This will require you to do an initial import for telims_pipe, but
    after that you will not need to reload individual modules, only the
    root module 'telims_pipe'.

This __init__ is for transport. If placed in maya/scripts directory, you
can simply: import telims_pipe. This __init__ will automatically append
the path to rigging_tools inside the sys.path list.
"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# third-party
from maya import cmds

# internal
import sys
import settings

#------------------------------------------------------------------------------#
#--------------------------------------------------------------------- START --#

# add telims_pipe to the PYTHONPATH variable for this session
sys.path.append(settings.root_path)
for directory in settings.directories:
    sys.path.append(directory)

# reset all modules
if globals().has_key('init_modules'):
    for m in [x for x in sys.modules.keys() if x not in init_modules]:
        del(sys.modules[m])
else:
    init_modules = sys.modules.keys()
