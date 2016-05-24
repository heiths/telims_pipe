#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    Maya utilities.
"""
#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# third-party
from maya import cmds

#------------------------------------------------------------------------------#
#----------------------------------------------------------------- FUNCTIONS --#

def find_all_incoming(start_nodes, max_depth=None):
    """
    Recursively finds all unique incoming dependencies for the specified node.
    """
    dependencies = set()
    _find_all_incoming(start_nodes, dependencies, max_depth, 0)
    return list(dependencies)

def _find_all_incoming(start_nodes, dependencies, max_depth, depth):
    """
    Recursively finds all unique incoming dependencies for the specified node.
    """
    if max_depth and depth > max_depth:
        return
    kwargs = dict(s=True, d=False)
    incoming = cmds.listConnections(list(start_nodes), **kwargs)
    if not incoming:
        return
    non_visitied = set(cmds.ls(incoming, l=True)).difference(dependencies)
    dependencies.update(non_visitied)
    if non_visitied:
        _find_all_incoming(non_visitied, dependencies, max_depth, depth + 1)

def find_all_outgoing(start_nodes, max_depth=None):
    """
    Recursively finds all unique outgoing dependents for the specified node.
    """
    dependents = set()
    _find_all_outgoing(start_nodes, dependents, max_depth, 0)
    return list(dependents)

def _find_all_outgoing(start_nodes, dependents, max_depth, depth):
    """
    Recursively finds all unique outgoing dependents for the specified node.
    """
    if max_depth and depth > max_depth:
        return
    kwargs = dict(s=True, d=False)
    outgoing = cmds.listConnections(list(start_nodes), **kwargs)
    if not outgoing:
        return  # ah the story of my life
    non_visitied = set(cmds.ls(outgoing, l=True)).difference(dependents)
    dependents.update(non_visitied)
    if non_visitied:
        _find_all_outgoing(non_visitied, dependents, max_depth, depth + 1)
