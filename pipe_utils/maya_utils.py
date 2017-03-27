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

# built-in
import sys
import os
import pymel.core as pm

# third-party
from maya import OpenMaya
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
        return
    non_visitied = set(cmds.ls(outgoing, l=True)).difference(dependents)
    dependents.update(non_visitied)
    if non_visitied:
        _find_all_outgoing(non_visitied, dependents, max_depth, depth + 1)

def find_top_parent(dag_object):
    """Finds the top parent of a dag object
        @PARAMS:
            dag_object: string
    """
    if not cmds.objExists(dag_object):
        return cmds.warning("Object '{0}' does not exist.".format(dag_object))
    dag_path = cmds.ls(dag_object, l=True)[0]
    return dag_path.split("|")[1]

def maya_tools_dir():
    """Returns users mayaToolDir path"""
    tools_path = cmds.internalVar(usd = True) + "mayaTools.txt"
    if os.path.exists(tools_path):
        f = open(tools_path, 'r')
        tools_path = f.readline()
        f.close()
        return tools_path

def select_geometry():
    """Selects all geometry in the scene and returns a list."""
    cmds.select(clear=True)
    relatives = cmds.listRelatives(cmds.ls(geometry=True), p=True, path=True)
    cmds.select(relatives, r=True)

    geometry = cmds.ls(sl=True, l=True)
    return geometry

def unused_materials(delete=None, material_type=None):
    """Deletes unused materials.
        @PARAMS:
            delete: boolean, True deletes materials.
            material_type: string, "phong".
        :NOTE: Delete unused Nodes in Maya failes due to a bug in the hypershade.
        Also, instead of wrapping try/except in here, wrap this function in
        a try/except using the epic logger.
    """
    # globals
    deleted_materials = list()
    ignore_materials = ["lambert1", "particleCloud1"]

    # find materials
    materials = cmds.ls(type=material_type)
    if not material_type:
        materials = cmds.ls(mat=True)

    # remove unused materials
    for material in materials:
        if (material in ignore_materials or
            material.startswith(("JointMover", "proxy_geo"))):
            continue
        cmds.hyperShade(objects=material)
        assigned_geo = cmds.ls(sl=True)
        if not assigned_geo:
            if delete:
                cmds.delete(material)
            deleted_materials.append(material)
    return deleted_materials

def reorder_outliner(objects=None):
    """Reorders the outliner based of selection.
        @PARAMS:
            objects: list, list of dag objects.
    """
    selection = cmds.ls(sl=True)
    if objects:
        selection = objects
    selection = sorted(selection, key=lambda s: s.lower())
    for dag_obj in selection:
        cmds.reorder(dag_obj, b=True)

def create_menu_item(label, parent, sub_menu, tear_off, divider):
    """Maya wrapper for creating menu items."""
    menu = cmds.menuItem(label, parent=parent, label=label,
                  subMenu=sub_menu, to=tear_off, divider=divider)
    return menu

def edit_menu_item(label, command):
    """Maya wrapper for adding commands to a menu."""
    label = label.replace(" ", "_")
    cmds.menuItem(label, e=True, command=command)

def get_associated_shader(mesh):
    """Returns  a list of associated shaders."""
    shapes = cmds.listRelatives(mesh, shapes=True, f=True)
    shading_groups = cmds.listConnections(shapes, type='shadingEngine')
    shaders = cmds.ls(cmds.listConnections(shading_groups), materials=True)
    return shaders

def get_file_paths(shader_list):
    """Takes in a list of shaders and finds all the 'file' attributes.
    Returns a dictionary of nodes and associated paths."""
    file_nodes_and_paths = dict()
    for shader in shader_list:
        history = cmds.listHistory(shader)
        for node in history:
            if cmds.nodeType(node) == 'file':
                file_path = cmds.getAttr(node + ".fileTextureName")
                file_nodes_and_paths[node] = file_path
    return file_nodes_and_paths

def find_skin_clusters(nodes):
    """Uses all incoming to search relatives to
    find associated skinCluster.
    @PARAMS:
        nodes: list
    """
    skin_clusters = list()
    if not isinstance(nodes, list):
        nodes = [nodes]
    relatives = cmds.listRelatives(nodes, ad=True, path=True)
    all_incoming = find_all_incoming(relatives)
    for node in all_incoming:
        if cmds.nodeType(node) == "skinCluster":
            if node not in skin_clusters:
                skin_clusters.append(node)
    return skin_clusters

def get_shape_node(node):
    """Finds the shape node from a selected transform node.
    @PARAMS:
        node: str, list"""
    if cmds.nodeType(node) != "transform":
        return
    shapes = cmds.listRelatives(node, shapes=True, path=True)
    if not shapes:
        message = "No shape node found. Intermediate? Handle this better Aaron."
        return OpenMaya.MGlobal_displayError(message)
    return shapes[0]

def get_mobject(name):
    """Get's MObject from given name."""
    selection_list = OpenMaya.MSelectionList()
    selection_list.add(name)
    mobject = OpenMaya.MObject()
    selection_list.getDependNode(0, mobject)
    return mobject

def hide_show_joints():
    active_view = pm.getPanel(withFocus=True)
    if pm.modelEditor(active_view, q=True, joints=True):
        pm.modelEditor(active_view, e=True, joints=False)
        return OpenMaya.MGlobal_displayInfo("Joints Hidden!")
    elif not pm.modelEditor(active_view, q=True, joints=True):
        pm.modelEditor(active_view, e=True, joints=True)
        return OpenMaya.MGlobal_displayInfo("Joints unhidden!")

def mirror_matching_control(from_curve=None, to_curve=None):
    # grab selection
    if not from_curve and not to_curve:
        selection = cmds.ls(sl=True)
        if len(selection) != 2:
            sel_message = "Please select two curves."
            return OpenMaya.MGlobal_displayWarning(sel_message)

        # get objects
        from_curve = selection[0]
        to_curve = selection[1]

    # calculate cvs
    from_degree = cmds.getAttr(from_curve + ".degree")
    from_spans = cmds.getAttr(from_curve + ".spans")
    from_number_of_cvs = from_degree + from_spans

    to_degree = cmds.getAttr(to_curve + ".degree")
    to_spans = cmds.getAttr(to_curve + ".spans")
    to_number_of_cvs = to_degree + to_spans

    if from_number_of_cvs != to_number_of_cvs:
        match_message = "Number of CV's do not match."
        return OpenMaya.MGlobal_displayWarning(match_message)

    # calculate points and invert world position (x)
    points = list()
    for cv in xrange(from_number_of_cvs):
        point_position = cmds.pointPosition("{0}.cv[{1}]".format(from_curve, cv))
        point_position[0] = - point_position[0]
        points.append(tuple(point_position))

    # apply to to_curve
    cmds.curve(to_curve, r=True, ws=True, p=points)

def convert_to_cloth_spheres():
    rigid_bodies = cmds.ls(type="nxRigidBody")
    if not cmds.pluginInfo("physx", q=True, l=True):
        plugin_warning = "Please load Physx Plugin."
        return OpenMaya.MGlobal.displayWarning(plugin_warning)
    if not rigid_bodies:
        rigid_warning = "Could not find any Rigid Bodies in Scene"
        return OpenMaya.MGlobal.displayWarning(rigid_warning)
    for rigid_body in rigid_bodies:
        shape_node = cmds.listRelatives(rigid_body, c=True)[0]
        cmds.setAttr("{0}.shapeType".format(shape_node), 6)

def mirror_rigid_body_transform():
    selection = cmds.ls(sl=True)[0]
    if "_r" in selection:
        _mirror_rigid_body_transform(selection, "_r", "_l")
    elif "_l" in selection:
        _mirror_rigid_body_transform(selection, "_l", "_r")

def _mirror_rigid_body_transform(selection, side, other_side):
    translates = ["tx", "ty", "tz"]
    mirror_node = selection.replace(side, other_side)
    if not cmds.objExists(mirror_node):
        message = "Couldn't find {0} mirror node".format(mirror_node)
        return OpenMaya.MGlobal_displayError(message)
    for trans in translates:
        translate = cmds.getAttr("{0}.{1}".format(selection, trans))
        cmds.setAttr("{0}.{1}".format(mirror_node, trans), -translate)

    radius = cmds.getAttr("{0}.radius".format(selection))
    cmds.setAttr("{0}.radius".format(mirror_node), radius)

