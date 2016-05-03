#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    telims menu.
"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# third-party
from maya import cmds, mel

# external
from rig_tools import curve_joint_generator
from pipe_ui import autorig_ui, joint_renamer_ui, overlap_tool_ui

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

def telims_menu(*args):
    """
    Builds and attaches menu to Maya.
    """
    # main window
    gMainWindow = mel.eval('$temp1 = $gMainWindow')

    # menu
    labels = list()
    menus = cmds.window(gMainWindow, q=True, menuArray=True)
    for menu in menus:
        label = cmds.menu(menu, q=True, l=True)
        labels.append(label)
    if "TELIMS" in labels:
        return
    telims_menu = cmds.menu(parent=gMainWindow, label='TELIMS')

    # menu items
    cmds.menuItem(parent=telims_menu, label='Autorig V1', c=autorig)
    cmds.menuItem(parent=telims_menu, label='Overlap Tool', c=overlap_tool)
    cmds.menuItem(parent=telims_menu, label='Joint Renamer', c=joint_renamer)
    cmds.menuItem(parent=telims_menu, label='Curve Joint Generator',
                  c=joints_on_a_curve)

def autorig(*args):
    """
    Autorig V1
    """
    initialize = autorig_ui.AutorigUI()
    tool = initialize.build_gui()

def joint_renamer(*args):
    """
    Joint Renamer
    """
    tool = joint_renamer_ui.JointRenamer()

def joints_on_a_curve(*args):
    """
    Tool for generating joints on a curve.
    """
    tool = curve_joint_generator.CurveJointGenerator()

def overlap_tool(*args):
    """
    Tool for building dynamic rigs onto FK rigs.
    """
    tool = overlap_tool_ui.OverlapToolUI()
