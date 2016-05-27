#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    abc_pipe setup.

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

def abc_setup_ui():
    """
    UI setup for abc pipe.
    """
    if cmds.window("abc_setup_ui", exists=True):
        cmds.delete("abc_setup_ui")

    # browse window
    window = cmds.window("abc_setup_ui", title='ABC Tools Install',
                         w=300, h=110, titleBarMenu=False, sizeable=False)

    # layouts
    main_layout = cmds.columnLayout(w = 300, h = 110)
    form_layout = cmds.formLayout(w = 300, h = 110)

    # notice
    text = cmds.text(label = "ERROR: Could not find ABC Tools directory. \n"
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
    Browse for abc_pipe directory.
    """
    abc_pipe_dir = cmds.fileDialog2(dialogStyle=2, fileMode=3)[0]

    #confirm that this is in fact the telims_pipe directory
    if os.path.split(abc_pipe_dir)[-1] != "abc_pipe":
        msg = "Selected directory is not the abc_pipe Directory, try again."
        return cmds.warning(msg)

    # build txt file containing path
    cmds.deleteUI("abc_setup_ui")
    path = cmds.internalVar(upd = True) + "abc_setup.txt"

    # write
    f = open(path, 'w')
    f.write(abc_pipe_dir)
    f.close()

    # setup menu
    abc_pipe_setup()

def cancel(*args):
    """
    Cancel search for abc_pipe.
    """
    cmds.deleteUI("abc_setup_ui")

def telims_pipe_setup():
    """
    Adds abc_pipe to PYTHON path variable.
    """
    path = cmds.internalVar(upd=True) + "abc_setup.txt"
    if os.path.exists(path):
        f = open(path, 'r')
        path = f.readline()
        if os.path.exists(path):
            if not path in sys.path:
                sys.path.append(path)

        # run setup
        setup_menus()
    else:
        abc_setup_ui()

def setup_menus():
    """
    Sets up ABC and comet menu.
    """
    # imports
    import abc_pipe
    import settings
    from pipe_ui.menus import abc_menu

    # menus
    menu = abc_menu.abc_menu()

    # add comet to MAYA_SCRIPT_PATH
    os.environ["MAYA_SCRIPT_PATH"] += str(";" + settings.COMET_TOOLS)
    mel.eval("source cometMenu.mel;")

# script job
scriptJobNum = cmds.scriptJob(event=["NewSceneOpened", abc_pipe_setup])
