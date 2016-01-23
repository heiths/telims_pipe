#!/usr/bin/env python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    Base module for generating hooks.

:use:
    from utils import name_utils
    name = name_utils.get_unique_name(char, side, node_type, suffix)
    loc = pm.spaceLocator(n=name)
"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
import pymel.core as pm

# external
import settings
from name_utils import NameUtils

#------------------------------------------------------------------------------#
#----------------------------------------------------------------- FUNCTIONS --#

class HookUtils(object):
    """
    Base class for handling hooks.
    """
    def __init__(self):
        """
        Initializer
        """
        pass

    @classmethod
    def create_hook(self, asset = "asset", side = "c",  part = "part",
                    snap_to = None, in_out = 'in', *args):
        """
        Settings for generating hooks in the autorig.

        :parameters:
            asset: For naming convention.
            side: For naming convention. (l, r, c)
            part: For naming convention.
            snap_to: Object to snap to.
            in_out: default value.

        :args:
            Please satisfy all arguements, args = security.
        """
        hook_name = NameUtils.get_unique_name(asset, side, part, "loc", args)
        hook = pm.createNode(settings.HOOK_NODE_TYPE, n=hook_name)

        if settings.HOOK_NODE_TYPE == "locator":
            hook = hook.getParent()
            hook.rename(hook_name)

        digit_type = 0
        if in_out == 'out':
            digit_type = 1

        hook.addAttr('hookType', at='float', dv=digit_type)
        hook.attr('hookType').lock(1)
        if snap_to:
            pm.xform(hook, ws=1, matrix=snap_to.wm.get())
        return hook
