#!/usr/bin/env python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    Base __init__ for rig_tools

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

# internal
import sys
import pipe_settings

#------------------------------------------------------------------------------#
#--------------------------------------------------------------------- START --#

# add telims_pipe to the PYTHONPATH variable for this session
sys.path.append(pipe_settings.root_path)

# reset all modules
if globals().has_key('init_modules'):
    for m in [x for x in sys.modules.keys() if x not in init_modules]:
        del(sys.modules[m])
else:
    init_modules = sys.modules.keys()

