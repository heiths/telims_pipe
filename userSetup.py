#!/usr/bin/env python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    telims_pipe setup.

:NOTE:
    No internal or external imports, it'll break the userSetup.
"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
import os
import sys

# third-party
import maya.cmds as cmds

#------------------------------------------------------------------------------#
#----------------------------------------------------------------- FUNCTIONS --#

def telims_setup_ui():
    """
    UI setup for telims pipe.
    """
    if cmds.window("telims_setup_ui", exists=True):
        cmds.delete("telims_setup_ui")

    # browse window
    window = cmds.window("telims_setup_ui", title='TELIMS Tools Install',
                         w=300, h=110, titleBarMenu=False, sizeable=False)

    # layouts
    main_layout = cmds.columnLayout(w = 300, h = 110)
    form_layout = cmds.formLayout(w = 300, h = 110)

    # notice
    text = cmds.text(label = "ERROR: Could not find TELIMS Tools directory. \n"
                     "Please locate using the \'Browse\' button.", w = 300)
    # buttons
    cancel_button = cmds.button(label="Cancel", w=140, h=50, c=cancel)
    browse_button = cmds.button(label="Browse", w=140, h=50, c=browse)

    # prep
    cancel_info = [(cancel_button, 'left', 5), (cancel_button, 'top', 50)]
    browse_info = [(browse_button, 'right', 5), (browse_button, 'top', 50)]
    text_info = [(text, 'left', 10), (text, 'top', 10)]

    # populate
    cmds.formLayout(form_layout, e=True, af=text_info)
    cmds.formLayout(form_layout, e=True, af=cancel_info)
    cmds.formLayout(form_layout, e=True, af=browse_info)

    cmds.showWindow(window)

def browse(*args):
    """
    Browse for telims_pipe directory.
    """
    telims_pipe_dir = cmds.fileDialog2(dialogStyle=2, fileMode=3)[0]

    #confirm that this is in fact the telims_pipe directory
    if os.path.split(telims_pipe_dir)[-1] != "telims_pipe":
        msg = "Selected directory is not the telims_pipe Directory, try again."
        return cmds.warning(msg)

    # build txt file containing path
    cmds.deleteUI("telims_setup_ui")
    path = cmds.internalVar(upd = True) + "telims_setup.txt"

    # write
    f = open(path, 'w')
    f.write(telims_pipe_dir)
    f.close()

    # setup menu
    telims_pipe_setup()

def cancel(*args):
    """
    Cancel search for telims_pipe.
    """
    cmds.deleteUI("telims_setup_ui")

def telims_pipe_setup():
    """
    Adds telims_pipe to PYTHON path variable.
    """
    path = cmds.internalVar(upd=True) + "telims_setup.txt"
    if os.path.exists(path):
        f = open(path, 'r')
        path = f.readline()
        if os.path.exists(path):
            if not path in sys.path:
                sys.path.append(path)

        # run setup
        setup_menus()
    else:
        telims_setup_ui()

def setup_menus():
    """
    Sets up telims and comet menu.
    """
    # imports
    import telims_pipe
    import settings
    from pipe_ui.menus import telims_menu

    # menus
    menu = telims_menu.telims_menu()

    # add comet to MAYA_SCRIPT_PATH
    os.environ["MAYA_SCRIPT_PATH"] += str(";" + settings.COMET_TOOLS)
    mel.eval("source cometMenu.mel;")

# script job
scriptJobNum = cmds.scriptJob(event=["NewSceneOpened", telims_pipe_setup])
