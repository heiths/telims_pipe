#!/usr/bin/env python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    Base module for zeroing out objects.

:use:

long description

"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
from maya import OpenMaya
import pymel.core as pm

# internal
from name_utils import NameUtils

#------------------------------------------------------------------------------#
#----------------------------------------------------------------- FUNCTIONS --#

def zero(obj, security=50):
    """
    This will group and zero out the transforms of an object.
    """
    parent = obj.getParent()
    name = obj.name()
    temp = name.split("_")

    # group name
    grp_name = NameUtils.get_unique_name(temp[0].split('0')[0],
                                          temp[1],
                                          temp[2].split('0')[0],
                                          "grp",
                                          security)
    if not grp_name:
        OpenMaya.MGlobal.displayError('ERROR generating name')
        return

    grp = pm.createNode("transform", n=grp_name)
    matrix = obj.wm.get()
    grp.setMatrix(matrix)

    # rebuild
    obj.setParent(grp)
    if parent:
        grp.setParent(par)
    return grp
