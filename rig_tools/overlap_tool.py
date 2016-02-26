#!/usr/bin/python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    This tool is for building an overlap rig on top of an FK rig.
    This tool will allow the animator to change the dynamics of the overlap
    rig as well as layer the FK controls on top. After the animation is
    satisfied, the animator may bake down the animation from the overlap
    rig to the original FK controls.

:use:
    from ani_tools.rmaya import overlap_tool
    tool = overlap_tool.OverlapTool()
    tool._build("tail_11_CON", ["tail_12_CON", "tail_13_CON"], 1, (1, 50))
    @params:
        rig_name: Name of the rig i.g. kongs_tail.
        parent_control: Parent Control
        selected_controls: The sequential order of the FK controls.
        point_lock: "base" = 0, "both-ends" = 1
        frame_range: Tuple (int(start), int(end))

TODO:
    - Batch Bake.
    - Batch Build.
    - Batch Delete.
    - Global Save and Load settings.
    - Part naming for multiple dynamic rigs in the scene.

:NOTES:
    The unique naming in this script is a fail safe. It'll be layered with
    individual rig naming conventions. So, if a user had two rig setups
    on the tail and named them both tail, the unique naming convention would
    ensure that they don't have any naming conflicts, i.e., tail_01 -> tail_02.
"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
import re
import json
from maya import cmds, mel

# external
from rig_tools.core import control

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- GLOBALS --#

CON = "constraint"
JOINT = "joint"
ATTRS = ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v")
TR_ATTRS = ("tx", "ty", "tz", "rx", "ry", "rz")
SCALE_ATTRS = ("sx", "sy", "sz")
LOCAL_SCALE_ATTRS = ("localScaleX", "localScaleY", "localScaleZ")

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class OverlapTool(object):
    """
    Tool for creating an overlap rig on top of an FK rig.
    """
    def __init__(self):
        """
        The Initializer
        """
        self.curve = None
        self.joints = list()
        self.controls = None
        self.base_ctrl = None
        self.selection = None
        self.root_group = None
        self.hair_system = None
        self.hair_group = list()
        self.fk_controls = list()
        self.parent_control = None
        self.dynamic_control = None
        self.dynamic_joints = list()
        self.dynamic_ik_curve = None

    def build(self, rig_name, parent_control, selected_controls,
              point_lock, frame_range):
        """
        Entry point.
        @params:
            rig_name: Name of rig.
            parent_control: Parent Control, space switching.
            selected_controls: The sequential order of the FK controls.
            point_lock: "base" = 0, "both-ends" = 1.
            frame_range: Tuple (int(start), int(end))
        """
        # initialize
        self.__init__()

        # data
        self.rig_name = rig_name
        self.parent_control = parent_control
        self.controls = selected_controls
        self.point_lock = point_lock
        self.start_frame = frame_range[0]
        self.end_frame = frame_range[1]

        # grab joints and build dynamic chain
        self._create_dynamic_control()
        dynamic_joint_chain = self._duplicate_joints("DyJnt")
        self.dynamic_joints = self._parent_joints(dynamic_joint_chain)
        self._create_curve(self.dynamic_joints)

        # build FK system
        fk_joint_chain = self._duplicate_joints("DyFKJnt")
        self.fk_joints = self._parent_joints(fk_joint_chain)
        self.fk_controls = self._build_fk_controls()
        self._connect_fk_controls()
        self._connect_fk_system()

        # begin dynamic build
        self._make_rig_dynamic()
        self._set_attributes()

        # transfer keys
        self._transfer_keys(self.controls, self.fk_controls)

        # hide everything but the controls
        self._hide()

        # finalize
        self._finalize()

    def bake(self, controls, frame_range):
        """
        Responsible for baking out the dynamic animation to the original rig.
        @params:
            controls: Controls that you're baking the animation onto.
            frame_range: Targeted frame range (int(start), int(end)).
        """
        start = frame_range[0]
        end = frame_range[1]

        # bake
        cmds.bakeResults(controls, sm=True, t=(start, end), at=TR_ATTRS)

    def delete(self, rig):
        """
        Delete root group and clear items in the selected controls.
        @param:
            rig: Object you want to delete (long path preferred).
        """
        if not rig:
            return

        # delete rig
        cmds.delete(rig)

        # clear meta nodes from scene
        meta_nodes = cmds.ls(type="network")
        for node in meta_nodes:
            if node.endswith("DyMETA"):
                cmds.delete(node)

    def _transfer_keys(self, from_controls, to_controls):
        """
        Responsible for the transfer of keys, given a provide frame range.
        @param:
            from_controls: Controls with keys you want to transfer.
            to_controls: Controls you want to transfer keys too.
        """
        start = self.start_frame
        end = self.end_frame
        for count, control in enumerate(from_controls):
            copy = cmds.copyKey(control, time=(start, end), at=TR_ATTRS)
            try:
                paste = cmds.pasteKey(to_controls[count], at=TR_ATTRS)
            except RuntimeError:
                continue

    def _build_fk_controls(self):
        """
        Builds the FK system for the Dynamic system.
        """
        controls = list()
        self.fk_groups = list()
        for count, joint in enumerate(self.fk_joints):
            control_name = self._get_unique_name("dynamicControl", "DyFKCtrl")
            control = cmds.spaceLocator(n=control_name)[0]
            cmds.setAttr("{0}.overrideEnabled".format(control), 1)
            cmds.setAttr("{0}.overrideColor".format(control), 13)
            for attr in SCALE_ATTRS:
                cmds.setAttr("{0}.{1}".format(control, attr), 10)
            controls.append(control)
            self._snap_control(control, False, joint, False)
            if count >= 1:
                cmds.parent(control, controls[count -1])
        if controls:
            fk_group_name = self._get_unique_name("dynamicControl", "DyFkGrp")
            self.fk_group = cmds.group(n=fk_group_name, em=True)
            cmds.parent(controls[0], self.fk_group)
        return controls

    def _connect_fk_controls(self):
        """
        Connects the FK system to the initially selected controls.
        """
        for count, joint in enumerate(self.fk_joints):
            cmds.parentConstraint(self.fk_controls[count], joint, mo=True)

        # constrain to dynamic joints for tranlation
        cmds.makeIdentity(self.dynamic_joints[0], apply=True)
        cmds.parentConstraint(self.fk_controls[0], self.dynamic_joints[0])

    def _make_rig_dynamic(self):
        """
        Responsible for creating the dynamic setup of the rig.
        """

        # make curve dynamic
        cmds.select(self.curve)
        make_curve = mel.eval('makeCurvesDynamic 2 {"1","0","1","1","0"}')

        # define hair system
        cmds.pickWalk(d="up")
        hair_system_name = self._get_unique_name("hairSystem", "DyHair")
        self.hair_system = cmds.rename(hair_system_name)
        cmds.parent(self.hair_system, self.pos_group)

        # rename and parent dynamic curve under dynamic control
        follicle_name = self._get_unique_name("dynamicFollicle", "DyFol")
        follicle = cmds.listRelatives(self.curve, p=True)
        self.follicle = cmds.rename(follicle, follicle_name)

        # point lock option
        point_lock_option = self.point_lock
        if point_lock_option == 1:
            cmds.setAttr("{0}Shape.pointLock".format(self.follicle), 3)
        elif point_lock_option == 0:
            cmds.setAttr("{0}Shape.pointLock".format(self.follicle), 1)

        # lets collect up our hair system
        transforms = cmds.ls(type="transform")
        dynamic_ik_curve_name = self._get_unique_name("dynamicIkCurve", "DyCrv")
        follicle_system_name = self._get_unique_name("follicleSystem", "DyFol")
        output_curve_group_name = self._get_unique_name("outputCurveSystem",
                                                        "DySys")
        for obj in transforms:
            if obj.startswith("hairSystem") and not obj.endswith("DySys"):
                if not obj.endswith("DyHair"):
                    cmds.parent(obj, self.pos_group)
                    self.hair_group.append(obj)
        # and rename
        for obj in self.hair_group:
            name = self._get_unique_name(str(obj), "DySys")
            new_name = cmds.rename(obj, name)
            if obj.endswith("OutputCurves"):
                self.output_curve_group = cmds.rename(new_name,
                                                      output_curve_group_name)
                relatives = cmds.listRelatives(self.output_curve_group, c=True)
                self.dynamic_ik_curve = cmds.rename(relatives[0],
                                                    dynamic_ik_curve_name)
            elif not obj.endswith("OutputCurves"):
                self.follicle_system = cmds.rename(new_name,
                                                   follicle_system_name)

        # define nucleus
        nucleus = cmds.ls(type="nucleus")
        nucleus_name = self._get_unique_name("dynamicNucleus", "DyNuc")
        for nuc in nucleus:
            if not nuc.endswith("DyNuc"):
                self.nucleus = cmds.rename(nuc, nucleus_name)
        cmds.parent(self.nucleus, self.pos_group)

        # create ikSplineSolver
        dynamic_ikSpline_name = self._get_unique_name("dynamicIkSpline", "DyIk")
        self.dynamic_ikSpline = cmds.ikHandle(sol="ikSplineSolver",
                                              ccv=False,
                                              roc=False,
                                              pcv=False,
                                              snc=True,
                                              sj=self.dynamic_joints[0],
                                              ee=self.dynamic_joints[-1],
                                              c=self.dynamic_ik_curve,
                                              n=dynamic_ikSpline_name)
        # parent ikHandle to dynamic control
        for item in self.dynamic_ikSpline:
            if item.endswith("DyIk"):
                cmds.parent(item, self.pos_group)

    def _connect_fk_system(self):
        """
        Skin FK joints to dynami curve.
        """
        fk_joints = self.fk_joints
        curve = self.curve
        skin_cluster_name = self._get_unique_name("dynamicCluster", "DyCtr")

        # select them in correct order and bind
        cmds.select(fk_joints, curve, r=True)
        cmds.skinCluster(n=skin_cluster_name, tsb=1, bm=0, sm=0, nw=1, wd=0,
                         mi=5, omi=1, dr=4, rui=1)

    def _set_attributes(self):
        """
        Add Dynamic Attributes to Dynamic Control.
        """
        # create the attributes
        dyCtrl = self.dynamic_control
        hairSys = self.hair_system
        fol = self.follicle

        # turn of Nuc Solver
        cmds.setAttr("{0}Shape.active".format(hairSys), 0)

        # let's begin
        self._dynamic_settings(dyCtrl, hairSys, fol)
        self._attraction_settings(dyCtrl, hairSys, fol)
        self._control_settings(dyCtrl, hairSys, fol)

    def _dynamic_settings(self, dyCtrl, hairSys, fol):
        """
        Responsible for setting the dynamic control attributes.
        """
        # header
        cmds.addAttr(dyCtrl, ln="dynamic", at="enum",
                     en="settings:", k=True)
        cmds.setAttr("{0}.dynamic".format(dyCtrl), l=True)

        # EN
        cmds.addAttr(dyCtrl, ln="EN", at="enum", en="on:off", k=True)

        # off
        cmds.setAttr("{0}.EN".format(dyCtrl), 1)
        cmds.setAttr("{0}Shape.simulationMethod".format(hairSys), 0)
        cmds.setDrivenKeyframe("{0}Shape.simulationMethod".format(hairSys),
                          "{0}.EN".format(dyCtrl))

        # on
        cmds.setAttr("{0}.EN".format(dyCtrl), 0)
        cmds.setAttr("{0}Shape.simulationMethod".format(hairSys), 3)
        cmds.setDrivenKeyframe("{0}Shape.simulationMethod".format(hairSys),
                          "{0}.EN".format(dyCtrl))

        # bend resistance
        cmds.addAttr(dyCtrl, ln="bendResistance", at="float",
                     dv=5, k=1, hnv=1, hxv=1)
        cmds.connectAttr("{0}.bendResistance".format(dyCtrl),
                         "{0}Shape.bendResistance".format(hairSys), f=1)

        # drag
        cmds.addAttr(dyCtrl, ln="drag", at="float",
                     dv=0.05, k=1, hnv=1, hxv=1)
        cmds.connectAttr("{0}.drag".format(dyCtrl),
                         "{0}Shape.drag".format(hairSys), f=1)

        # damp
        cmds.addAttr(dyCtrl, ln="damp", at="float",
                     dv=0, k=1, hnv=1, hxv=1)
        cmds.connectAttr("{0}.damp".format(dyCtrl),
                         "{0}Shape.damp".format(hairSys), f=1)

        # start frame (nucleus)
        cmds.addAttr(dyCtrl, ln="startFrame", at="long",
                     dv=self.start_frame, k=1, hnv=1, hxv=1)
        cmds.connectAttr("{0}.startFrame".format(dyCtrl),
                         "{0}.startFrame".format(self.nucleus))

        # space scale
        # cmds.addAttr(dyCtrl, ln="spaceScale", at="float",
                     # dv=0.01, k=1, hnv=1, hxv=1)
        # cmds.connectAttr("{0}.spaceScale".format(dyCtrl),
                         # "{0}.spaceScale".format(self.nucleus))

    def _attraction_settings(self, dyCtrl, hairSys, fol):
        """
        Responsible for setting the start curve attract attraction settings.
        """
        # header
        cmds.addAttr(dyCtrl, ln="attraction", at="enum",
                     en="settings:", k=True)
        cmds.setAttr("{0}.attraction".format(dyCtrl), l=True)

        # start curve attract
        cmds.addAttr(dyCtrl, ln="startCurveAttract", at="float",
                     dv=0.2, k=1, hnv=1, hxv=1)
        cmds.connectAttr("{0}.startCurveAttract".format(dyCtrl),
                         "{0}Shape.startCurveAttract".format(hairSys), f=1)

        # attraction attributes
        positions = list()
        for count, control in enumerate(self.fk_controls):
            position = float(count)/len(self.fk_controls)
            positions.append(position)
        positions.append(1)
        values = list(reversed(positions))
        for count, control in enumerate(self.fk_controls):
            position = positions[count]
            value = values[count]

            cmds.addAttr(dyCtrl, ln="attraction_0{0}".format(count),
                         at="float", dv=value, k=1, hnv=1, hxv=1)
            cmds.setAttr("{0}Shape.attractionScale[{1}]."\
                         "attractionScale_Position".format(hairSys, count),
                         position)
            cmds.connectAttr("{0}.attraction_0{1}".format(dyCtrl, count),
                 "{0}Shape.attractionScale[{1}]."\
                 "attractionScale_FloatValue".format(hairSys, count))
            cmds.setAttr("{0}Shape.attractionScale[{1}]."\
                         "attractionScale_Interp".format(hairSys, count), 3)
        # last position
        last_pos = len(positions)
        cmds.addAttr(dyCtrl, ln="attraction_0{0}".format(last_pos - 1),
                     at="float", dv=0, k=1, hnv=1, hxv=1)
        cmds.setAttr("{0}Shape.attractionScale[{1}]."\
                     "attractionScale_Position".format(hairSys, last_pos),
                     1)
        cmds.connectAttr("{0}.attraction_0{1}".format(dyCtrl, last_pos - 1),
             "{0}Shape.attractionScale[{1}]."\
             "attractionScale_FloatValue".format(hairSys, last_pos))
        cmds.setAttr("{0}Shape.attractionScale[{1}]."\
                     "attractionScale_Interp".format(hairSys, last_pos), 3)

    def _control_settings(self, dyCtrl, hairSys, fol):
        """
        Responsible for setting the control attributes.
        """
        # header
        cmds.addAttr(dyCtrl, ln="control",at="enum",
                     en="Settings:", k=True)
        cmds.setAttr("{0}.control".format(dyCtrl), l=True)
        cmds.addAttr(dyCtrl, ln="scaleControls", at="float",
                     dv=1, k=True)

        # scale locators
        for control in self.fk_controls:
            for attr in LOCAL_SCALE_ATTRS:
                cmds.connectAttr("{0}.scaleControls".format(dyCtrl),
                                 "{0}Shape.{1}".format(control, attr))
        cmds.addAttr(dyCtrl, ln="scaleDynamicControl", at="float",
                     dv=1, k=True)

        # scale dynamic control
        for attr in SCALE_ATTRS:
            cmds.connectAttr("{0}.scaleDynamicControl".format(dyCtrl),
                             "{0}.{1}".format(dyCtrl, attr))

    def _hide(self):
        """
        Hides everything but the dynamic control.
        """
        system = cmds.listRelatives(self.pos_group, ad=True)
        for item in system:
            if not re.search("DyCtrl|DyFKCtrl", item, re.I):
                try:
                    cmds.hide(item)
                except ValueError:
                    continue

    def _get_joints(self, base_ctrl):
        """
        Responsible for collecting up all corrisponding joints based on
        selected controls.
        """
        # filter through connections
        inbetween_joints = list()
        for control in self.controls:
            joint = cmds.listConnections(control, type=JOINT)
            if not joint:
                joint = cmds.listConnections(control, type=CON)
                joint = cmds.listConnections(joint, type=JOINT)
            try:
                joint = list(set(joint))
                inbetween_joints.append(joint[0])
            except TypeError:
                continue

        # result
        return inbetween_joints

    def _duplicate_joints(self, suffix):
        """
        Duplicate joints.
        @param:
            suffix: Suffix of joint chain.
        """
        joint_chain = list()
        for control in self.controls:
            joint_name = self._get_unique_name("dynamicChain", suffix)
            position = cmds.xform(control, q=True, ws=True, rp=True)
            rotation = cmds.xform(control, q=True, ws=True, ro=True)
            # must clear selection
            cmds.select(cl=True)
            joint = cmds.joint(n=joint_name, p=position, o=rotation)
            joint_chain.append(joint)

        # parent joints
        return joint_chain

    def _parent_joints(self, joint_chain):
        """
        Responsible for parenting the dynamic joints into a hierarchy.
        """
        joint_chain = list(reversed(joint_chain))
        for count in range(len(joint_chain)):
            if count != len(joint_chain)-1:
                try:
                    cmds.parent(joint_chain[count],
                                joint_chain[count + 1])
                except (RuntimeError, ValueError):
                    break

        # group joints to root group
        joint_chain = list(reversed(joint_chain))
        cmds.parent(joint_chain[0], self.pos_group)
        cmds.makeIdentity(joint_chain[0], apply=True)
        return joint_chain

    def _create_curve(self, joint_chain):
        """
        Responsible for creating the dynamic curve for the IK Spline solver.
        """
        # create our curve
        curve_name = self._get_unique_name("dynamicCurve", "DyCrv")
        self.joint_positions = list()
        for joint in joint_chain:
            joint_pos = cmds.xform(joint, q=True, ws=True, t=True)
            self.joint_positions.append(joint_pos)
        tmp_curve = cmds.curve(d=3, ep=self.joint_positions)
        tmp_curve = cmds.rename(tmp_curve, curve_name)
        self.curve = cmds.rebuildCurve(tmp_curve, s=len(joint_chain)*3,
                                       ch=False)

    def _create_dynamic_control(self):
        """
        Creates the dynamic main control as well as the root group.
        """
        # make control and groups
        dynamic_control_name = self._get_unique_name("dynamicControl", "DyCtrl")
        root_group_name = self._get_unique_name("dynamicRig", "DyROOT")
        pos_group_name = self._get_unique_name("dynamicControl", "DyPOS")

        self.root_group = cmds.group(n=root_group_name, empty=True)
        self.pos_group = cmds.group(n=pos_group_name, empty=True)
        self.dynamic_control = control.createControl(shape="cube",
                                                     color="yellow",
                                                     scale=10,
                                                     n=dynamic_control_name)

        # root control
        target = self.controls[0]

        # snap control
        self._snap_control(self.dynamic_control, self.pos_group, target, True)
        cmds.parent(self.pos_group, self.root_group)

    def _snap_control(self, control, group, target, history):
        """
        Handles snapping controls.
        """
        snap_tuple = (control, group)
        if not group:
            snap_tuple = (control,)
        # snap the control
        for obj in snap_tuple:
            tmp_constraint = cmds.parentConstraint(target, obj)
            cmds.delete(tmp_constraint)
        if group:
            cmds.parent(control, group)
        if history:
            cmds.makeIdentity(control, apply=True)
        else:
            cmds.makeIdentity(control, apply=True, t=True)
        cmds.DeleteHistory(control)

    def _finalize(self):
        """
        Finish up the rig by connecting it to the actual rig.
        """
        # connect
        cmds.parent(self.fk_group, self.pos_group)
        cmds.parentConstraint(self.fk_controls[0], self.dynamic_control)
        for item in (self.fk_group, self.dynamic_joints[0]):
            cmds.parentConstraint(self.parent_control, item, mo=True)
        for count, control in enumerate(self.controls):
            cmds.parentConstraint(self.dynamic_joints[count], control, mo=False)

        # lock and hide attributes on dynamic control
        for attr in ATTRS:
            cmds.setAttr("{0}.{1}".format(self.dynamic_control, attr),
                         l=True, k=False, cb=False)
        self._create_meta_data()

    def _create_meta_data(self):
        """
        Creates a network node to hold the meta data for the rig.
        """
        network_node = cmds.createNode("network")
        meta_node_name = self._get_unique_name("metaNode", "DyMETA")
        meta_node = cmds.rename(network_node, meta_node_name)
        data = {
                "rigName" : self.rig_name,
                "parentControl" : self.parent_control,
                "controls" : self.controls,
                "pointLock" : self.point_lock,
                "startFrame" : self.start_frame,
                "endFrame" : self.end_frame}
        # build data
        for meta, data in data.iteritems():
            if meta == "controls":
                cmds.addAttr(meta_node, dt="stringArray", ln=meta)
                cmds.setAttr("{0}.{1}".format(meta_node, meta),
                             *([len(data)]+data), type="stringArray")
                continue
            cmds.addAttr(meta_node, dt="string", ln=meta)
            cmds.setAttr("{0}.{1}".format(meta_node, meta),
                         data, type="string")

    def _get_unique_name(self, obj_type, suffix):
        """
        Basic name generator to prevent duplicates or name conflicts.
        @params:
            obj_type: The type of object you're naming i.e., dynamicControl.
            suffix: Suffix of object you're naming i.e., DyCtrl.
        """
        rig_name = self.rig_name
        name = '{0}_{1}0{2}_{3}'.format(rig_name, obj_type, str(1), suffix)
        count = 1
        while cmds.objExists(name):
            count+=1
            name = '{0}_{1}0{2}_{3}'.format(rig_name, obj_type, count, suffix)
        return name

    def _json_save(self, data=None, path=None):
        """
        Saves out given data into a json file.
        """
        if not path:
            path = cmds.fileDialog2(fm=0, ds=2, ff="*.json", rf=True)
            if not path:
                return
            path = path[0]

        data = json.dumps(data, sort_keys=True, ensure_ascii=True, indent=2)
        fobj = open(path, 'w')
        fobj.write(data)
        fobj.close()

        return path

    def _json_load(self, path=None):
        """
        This procedure loads and returns the content of a json file.
        """
        if not path:
            path = cmds.fileDialog2(fm=1, ds=2, ff="*.json")
            if not path:
                return
            path = path[0]

        fobj = open(path)
        data = json.load(fobj)
        return data
