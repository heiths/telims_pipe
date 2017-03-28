#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle
:description:
    A fast and efficient skinWeight manager using the Python Maya API.

:how to use:
    import abc_pipe
    from rig_utils import skin_weight_manager

    # export weights
    path = "path/to/export/{0}.json"
    selection = cmds.ls(sl=True)
    if selection:
        for selected_geo in selection:
            path = path.format(selected_geo)
            skin_weight_manager.export_skin_weights(path)

    # import weights
    path = "path/to/export/{0}.json"
    selection = cmds.ls(sl=True)
    removed_unused = None # or True
    if selection:
        for selected_geo in selection:
            path = path.format(selected_geo)
            skin_weight_manager.import_skin_weights(path,
                                   remove_unused=remove_unused)

:API reference:
    http://help.autodesk.com/view/MAYAUL/2016/ENU/?guid=__py_ref_index_html

:see also:
    TODO:
        ui/skin_weight_manager_ui.py
"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
import os

# third-party
from maya import cmds
from maya import OpenMaya, OpenMayaAnim

# external
from pipe_utils.string_utils import remove_namespace
from pipe_utils.maya_utils import find_skin_clusters, get_mobject
from pipe_utils.system_utils import json_save, json_load, win_path_convert

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- GLOBALS --#

ATTRIBUTES = ['skinningMethod', 'normalizeWeights', 'dropoffRate',
              'maintainMaxInfluences', 'maxInfluences','bindMethod',
              'useComponents', 'normalizeWeights', 'weightDistribution',
              'heatmapFalloff']

#------------------------------------------------------------------------------#
#----------------------------------------------------------------- FUNCTIONS --#

def _vert_check(data, geometry):
    # check vertex count
    for skin_data in data:
        geometry = skin_data["shape"]
        vert_count = cmds.polyEvaluate(geometry, vertex=True)
        import_vert_count = len(skin_data["blendWeights"])
        if vert_count != import_vert_count:
            geo = geometry
            vert_message = "The vert count does not match for {0}.".format(geo)
            return OpenMaya.MGlobal_displayError(vert_message)
    return True

def _geometry_check(geometry):
    if not geometry:
        geometry = cmds.ls(sl=True)
    if cmds.nodeType(geometry) != "transform" or not geometry:
        geo_message = "Please select a piece/s of geometry."
        return OpenMaya.MGlobal_displayError(geo_message)
    return geometry

def export_skin_weights(file_path=None, geometry=None):
    """Exports out skin weight from selected geometry"""
    data = list()
    # error handling
    if not file_path:
        return OpenMaya.MGlobal_displayError("No file path given.")
    if not geometry:
        geometry = _geometry_check(geometry)
        if not geometry:
            return

    # build up skin data
    skin_clusters = find_skin_clusters(geometry)
    if not skin_clusters:
        skin_message = "No skin clusters found on {0}.".format(geometry)
        return OpenMaya.MGlobal_displayWarning(skin_message)
    for skin_cluster in skin_clusters:
        skin_data_init = SkinData(skin_cluster)
        skin_data = skin_data_init.gather_data()
        data.append(skin_data)
        args = [skin_data_init.skin_cluster, file_path]
        export_message = "SkinCluster: {0} has " \
                         "been exported to {1}.".format(*args)
        OpenMaya.MGlobal_displayInfo(export_message)

    # dump data
    file_path = win_path_convert(file_path)
    json_save(data, file_path)

def import_skin_weights(file_path=None, geometry=None, remove_unused=None):
    # load data
    if not file_path:
        return OpenMaya.MGlobal_displayError("No file path given.")
    if not os.path.exists(file_path):
        path_message = "Could not find {0} file.".format(file_path)
        return OpenMaya.MGlobal_displayWarning(path_message)
    data = json_load(file_path)

    # geometry handling
    if not geometry:
        geometry = _geometry_check(geometry)
        if not geometry:
            return
    else:
        data[0]["shape"] = geometry

    # check verts
    vert_check = _vert_check(data, geometry)
    if not vert_check:
        return

    # import skin weights
    _import_skin_weights(data, geometry, file_path, remove_unused)

def _import_skin_weights(data, geometry, file_path, remove_unused=None):

    # loop through skin data
    for skin_data in data:
        geometry = skin_data["shape"]
        if not cmds.objExists(geometry):
            continue

        skin_clusters = find_skin_clusters(geometry)
        if skin_clusters:
            skin_cluster = SkinData(skin_clusters[0])
            skin_cluster.set_data(skin_data)
        else:
            # TODO: make joint remapper, Chris has a setup for this already
            skin_cluster = _create_new_skin_cluster(skin_data, geometry)
            if not skin_cluster:
                continue
            skin_cluster[0].set_data(skin_data)
        if remove_unused:
            if skin_clusters:
               _remove_unused_influences(skin_clusters[0])
            else:
                _remove_unused_influences(skin_cluster[1])
        OpenMaya.MGlobal_displayInfo("Imported {0} onto {1}.".format(file_path, geometry))

def _remove_unused_influences(skin_cluster):
    influences_to_remove = list()
    weighted_influences = cmds.skinCluster(skin_cluster, q=True, wi=True)
    final_transforms = cmds.skinCluster(skin_cluster, q=True, inf=True)
    for influence in final_transforms:
        if influence not in weighted_influences:
            influences_to_remove.append(influence)
    for influence in influences_to_remove:
        cmds.skinCluster(skin_cluster, e=True, ri=influence)

def _create_new_skin_cluster(skin_data, geometry):
    # check joints
    joints = skin_data["weights"].keys()
    unused_joints = list()
    scene_joints = set([remove_namespace(joint) for joint \
                        in cmds.ls(type="joint")])
    for joint in joints:
        if not joint in scene_joints:
            unused_joints.append(joint)
    # TODO: make joint remapper, Chris has a setup for this already
    if unused_joints and not scene_joints:
        return

    skin_cluster = cmds.skinCluster(joints, geometry, tsb=True, nw=2,
                                    n=skin_data["skinCluster"])[0]
    return (SkinData(skin_cluster), skin_cluster)

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class SkinData(object):
    def __init__(self, skin_cluster):

        # globals/data
        self.skin_cluster = skin_cluster
        deformer = cmds.deformer(skin_cluster, q=True, g=True)[0]
        self.shape = cmds.listRelatives(deformer, parent = True, path=True)[0]
        self.mobject = get_mobject(self.skin_cluster)
        self.skin_set = OpenMayaAnim.MFnSkinCluster(self.mobject)
        self.data = {
            "weights" : dict(),
            "blendWeights" : list(),
            "skinCluster" : self.skin_cluster,
            "shape" : self.shape
            }

    def gather_data(self):

        # get incluence and blend weight data
        dag_path, mobject = self.get_skin_dag_path_and_mobject()
        self.get_influence_weights(dag_path, mobject)
        self.get_blend_weights(dag_path, mobject)

        # add in attribute data
        for attribute in ATTRIBUTES:
            self.data[attribute] = cmds.getAttr("{0}.{1}". \
                                        format(self.skin_cluster,
                                               attribute))
        return self.data

    def get_skin_dag_path_and_mobject(self):
        function_set = OpenMaya.MFnSet(self.skin_set.deformerSet())
        selection_list = OpenMaya.MSelectionList()
        function_set.getMembers(selection_list, False)
        dag_path = OpenMaya.MDagPath()
        mobject = OpenMaya.MObject()
        selection_list.getDagPath(0, dag_path, mobject)
        return dag_path, mobject

    def get_influence_weights(self, dag_path, mobject):
        weights = self._get_weights(dag_path, mobject)

        influence_paths = OpenMaya.MDagPathArray()
        influence_count = self.skin_set.influenceObjects(influence_paths)
        components_per_influence = weights.length() / influence_count
        for count in xrange(influence_paths.length()):
            name = influence_paths[count].partialPathName()
            name = remove_namespace(name)
            weight_data = [weights[influence*influence_count+count] \
                           for influence in xrange(components_per_influence)]
            self.data["weights"][name] = weight_data

    def _get_weights(self, dag_path, mobject):
        """Where the API magic happens."""
        weights = OpenMaya.MDoubleArray()
        util = OpenMaya.MScriptUtil()
        util.createFromInt(0)
        pointer = util.asUintPtr()

        # magic call
        self.skin_set.getWeights(dag_path, mobject, weights, pointer);
        return weights

    def get_blend_weights(self, dag_path, mobject):
        return self._get_blend_weights(dag_path, mobject)

    def _get_blend_weights(self, dag_path, mobject):
        weights = OpenMaya.MDoubleArray()

        # magic call
        self.skin_set.getBlendWeights(dag_path, mobject, weights)
        blend_data = [weights[blend_weight] for \
                      blend_weight in xrange(weights.length())]
        self.data["blendWeights"] = blend_data

    def set_data(self, data):
        """Final point for importing weights. Sets and applies influences
        and blend weight values.
        @PARAMS:
            data: dict()
        """
        self.data = data
        dag_path, mobject = self.get_skin_dag_path_and_mobject()
        self.set_influence_weights(dag_path, mobject)
        self.set_blend_weights(dag_path, mobject)

        # set skinCluster Attributes
        for attribute in ATTRIBUTES:
            cmds.setAttr('{0}.{1}'.format(self.skin_cluster, attribute),
                         self.data[attribute])

    def set_influence_weights(self, dag_path, mobject):
        weights = self._get_weights(dag_path, mobject)
        influence_paths = OpenMaya.MDagPathArray()
        influence_count = self.skin_set.influenceObjects(influence_paths)
        components_per_influence = weights.length() / influence_count

        # influences
        unused_influences = list()
        influences = [influence_paths[inf_count].partialPathName() for \
                      inf_count in xrange(influence_paths.length())]

        # build influences/weights
        for imported_influence, imported_weights in self.data['weights'].items():
            for inf_count in xrange(influence_paths.length()):
                influence_name = influence_paths[inf_count].partialPathName()
                influence_name = remove_namespace(influence_name)
                if influence_name == imported_influence:
                    # set the weights
                    for count in xrange(components_per_influence):
                        weights.set(imported_weights[count],
                                    count * influence_count + inf_count)
                    influences.remove(influence_name)
                    break
            else:
                unused_influences.append(imported_influence)

        # TODO: make joint remapper
        if unused_influences and influences:
            OpenMaya.MGlobal_displayWarning("Make a joint remapper, Aaron!")

        # set influences
        influence_array = OpenMaya.MIntArray(influence_count)
        for count in xrange(influence_count):
            influence_array.set(count, count)
        # set weights
        self.skin_set.setWeights(dag_path, mobject, influence_array, weights, False)

    def set_blend_weights(self, dag_path, mobject):
        blend_weights = OpenMaya.MDoubleArray(len(self.data['blendWeights']))
        for influence, weight in enumerate(self.data['blendWeights']):
            blend_weights.set(weight, influence)
        self.skin_set.setBlendWeights(dag_path, mobject, blend_weights)
