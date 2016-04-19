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
    tool._build(params)
    @params:
        rig_name, string: Name of the rig i.g. kongs_tail.
        parent_control, string: Parent Control
        selected_controls, list: The sequential order of the FK controls.
        point_lock, int: "base" = 0, "both-ends" = 1
        frame_range: Tuple (int(start), int(end))

:see also:
    ani_tools/ui/overlap_tool_ui.py

TODO:
    - Batch Build.
    - Global Save and Load settings (presets).

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

# third party
from PyQt4 import QtGui, QtCore

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
        self.nucleus = None
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
        dynamic_joint_chain = self._build_joints("DyJnt")
        self.dynamic_joints = self._parent_joints(dynamic_joint_chain)
        self._create_curve(self.dynamic_joints)

        # build FK system
        fk_joint_chain = self._build_joints("DyFKJnt")
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

    def batch_bake(self, frame_range=None):
        """
        Bakes out all rigs in the scene.
        @params:
            frame_range: If no frame range give, it will bake based on scene.
        """
        if not frame_range:
            self.start_frame = cmds.playbackOptions(q=True, min=True)
            self.end_frame = cmds.playbackOptions(q=True, max=True)

        # grab controls
        controls = self.find_meta_attribute("controls")

        # bake
        if controls:
            self.bake(controls, frame_range)

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

        # delete meta node
        for node in cmds.ls(type="network"):
            if node.endswith("DyMETA"):
                root_group = cmds.getAttr("{0}.rootGroup".format(node))
                if root_group == rig:
                    cmds.delete(node)

    def batch_delete(self):
        """
        Deletes all overlap rigs in the scene.
        """
        # delete all dynamic rigs
        rigs = self.find_meta_attribute("rootGroup")
        for rig in rigs:
            cmds.delete(rig)
        for node in cmds.ls(type="network"):
            if node.endswith("DyMETA"):
                cmds.delete(node)

    def find_meta_attribute(self, attribute):
        """
        Tool for finding specific meta data.
        """
        # find rigs
        meta = list()
        meta_nodes = cmds.ls(type="network")
        for node in meta_nodes:
            if node.endswith("DyMETA"):
                value = cmds.getAttr("{0}.{1}".format(node, attribute))
                if attribute == "controls":
                    meta.extend(value)
                    continue
                meta.append(value)
        if attribute == "controls":
            return meta
        return list(set(meta))

    def _transfer_keys(self, from_controls, to_controls):
        """
        Responsible for the transfer of keys, given a provided frame range.
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
        NOTE:
            Using the worldspace based on the controls will not be good enough.
            In order to maintain local translations that match the original
            control, the world space must be grabbed from the transform holding
            the transforms for the control. Also, the local transforms on
            the new locator controls must match those on the FK control. If
            they don't, copying keys will offset the controls.
        """
        locators = list()
        groups = list()
        for count, joint in enumerate(self.fk_joints):
            cmds.select(cl=True)

            # naming
            locator_name = self._get_unique_name("dynamicControl", "DyFKCtrl")
            group_name = self._get_unique_name("dynamicControl", "DyFKCtrlGrp")

            # global and local transforms
            control = self.controls[count]
            parent = cmds.listRelatives(control, p=True)
            pad_position = cmds.xform(control, q=True, ws=True, rp=True)
            pad_rotation = cmds.xform(control, q=True, ws=True, ro=True)
            if parent:
                pad_position = cmds.xform(parent, q=True, ws=True, rp=True)
                pad_rotation = cmds.xform(parent, q=True, ws=True, ro=True)
            loc_position = cmds.xform(control, q=True, os=True, rp=True)
            loc_rotation = cmds.xform(control, q=True, os=True, ro=True)

            # build control
            locator = cmds.spaceLocator(n=locator_name)[0]
            group = cmds.group(n=group_name, em=True)
            cmds.parent(locator, group)

            # snap and maintain key offset
            cmds.xform(group, ws=True, t=pad_position)
            cmds.xform(group, ws=True, ro=pad_rotation)
            cmds.xform(locator, os=True, t=loc_position)
            cmds.xform(locator, os=True, ro=loc_rotation)

            # colorize
            cmds.setAttr("{0}.overrideEnabled".format(locator), 1)
            cmds.setAttr("{0}.overrideColor".format(locator), 13)
            for attr in SCALE_ATTRS:
                cmds.setAttr("{0}.{1}".format(locator, attr), 10)

            # retain
            locators.append(locator)
            groups.append(group)

        # build hierarchy
        for count, locator in enumerate(locators, 1):
            if count == len(groups):
                break
            cmds.parent(groups[count], locator)

        # parent to rig hierarchy
        fk_group_name = self._get_unique_name("dynamicControl", "DyFkGrp")
        self.fk_group = cmds.group(n=fk_group_name, em=True)
        cmds.parent(groups[0], self.fk_group)

        return locators

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
        if self.nucleus:
            cmds.parent(self.nucleus, self.pos_group)

        # create ikSplineSolver accounting for motion path contstraints
        dynamic_ikSpline_name = self._get_unique_name("dynamicIkSpline", "DyIk")
        self.dynamic_ikSpline = cmds.ikHandle(sol="ikSplineSolver", ccv=False,
                                              roc=False, pcv=False,
                                              snc=False, cra=True,
                                              sj=self.dynamic_joints[0],
                                              ee=self.dynamic_joints[-1],
                                              c=self.dynamic_ik_curve,
                                              n=dynamic_ikSpline_name)
        # parent ikHandle to dynamic control
        for item in self.dynamic_ikSpline:
            if item.endswith("DyIk"):
                cmds.parent(item, self.pos_group)

        # parent joints back to main group with new transform node
        parent = cmds.listRelatives(self.dynamic_joints[0], p=True)
        motion_parent_name = self._get_unique_name("dynamicChain", "DyJntGrp")
        self.motion_parent = cmds.rename(parent, motion_parent_name)
        cmds.parent(self.motion_parent, self.pos_group)

    def _connect_fk_system(self):
        """
        Skin FK joints to dynamic curve.
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
        nuc = self.nucleus

        # turn off Nuc Solver and set start frame
        cmds.setAttr("{0}Shape.active".format(hairSys), 0)
        cmds.setAttr("{0}.startFrame".format(nuc), self.start_frame)

        # let's begin
        self._dynamic_settings(dyCtrl, hairSys, fol)
        self._attraction_settings(dyCtrl, hairSys, fol)
        self._stiffness_settings(dyCtrl, hairSys, fol)
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

        # motion drag
        cmds.addAttr(dyCtrl, ln="motionDrag", at="float", k=1, hnv=1, hxv=1)
        cmds.connectAttr("{0}.motionDrag".format(dyCtrl),
                         "{0}Shape.motionDrag".format(hairSys), f=1)

        # drag
        cmds.addAttr(dyCtrl, ln="drag", at="float",
                     k=1, hnv=1, hxv=1)
        cmds.connectAttr("{0}.drag".format(dyCtrl),
                         "{0}Shape.drag".format(hairSys), f=1)

        # damp
        cmds.addAttr(dyCtrl, ln="damp", at="float",
                     dv=0, k=1, hnv=1, hxv=1)
        cmds.connectAttr("{0}.damp".format(dyCtrl),
                         "{0}Shape.damp".format(hairSys), f=1)

        # iterations
        cmds.addAttr(dyCtrl, ln="iterations", at="float", k=1, hnv=1, hxv=1)
        cmds.connectAttr("{0}.iterations".format(dyCtrl),
                         "{0}Shape.iterations".format(hairSys), f=1)

        # stiffness
        cmds.addAttr(dyCtrl, ln="stiffness", at="float", k=0, hnv=1, hxv=1,
                     dv=1, min=0, max=1)
        cmds.connectAttr("{0}.stiffness".format(dyCtrl),
                         "{0}Shape.stiffness".format(hairSys), f=1)

    def _attraction_settings(self, dyCtrl, hairSys, fol):
        """
        Responsible for setting the start curve attract attraction settings.
        """
        # start curve attract
        cmds.addAttr(dyCtrl, ln="startCurveAttract", at="float",
                     dv=1, k=0, hnv=1, hxv=1)
        cmds.connectAttr("{0}.startCurveAttract".format(dyCtrl),
                         "{0}Shape.startCurveAttract".format(hairSys), f=1)

        # header
        cmds.addAttr(dyCtrl, ln="scaleAttraction", at="enum",
                     en="settings:", k=True)
        cmds.setAttr("{0}.scaleAttraction".format(dyCtrl), l=True)

        # begin attribute setting
        self._scale_settings(dyCtrl, hairSys, fol, "attractionScale")

    def _stiffness_settings(self, dyCtrl, hairSys, fol):
        """
        Responsible for setting the stiffness scale settings.
        """
        # header
        cmds.addAttr(dyCtrl, ln="scaleStiffness", at="enum",
                     en="settings:", k=True)
        cmds.setAttr("{0}.scaleStiffness".format(dyCtrl), l=True)

        # begin attribute setting
        self._scale_settings(dyCtrl, hairSys, fol, "stiffnessScale")

    def _scale_settings(self, dyCtrl, hairSys, fol, scale_attribute):
        """
        Responsible for setting the start curve attract attraction settings.
        """
        # attraction attributes
        positions = list()
        end_name = scale_attribute.split("Scale")[0].capitalize()
        if end_name == "Stiffness":
            end_name = "Stiff"
        elif end_name == "Attraction":
            end_name = "Attract"

        # inital values
        for count in xrange(5):
            position = float(count)/5
            positions.append(position)
        positions.append(1)
        values = list(reversed(positions))

        # set attributes
        for count in xrange(5):
            if count == 0:
                attribute = "{0}{1}".format(end_name, "Start")
            else:
                attribute = "{0}0{1}".format(end_name, count)
            position = positions[count]
            value = values[count]
            cmds.addAttr(dyCtrl, ln=attribute, at="float",
                         dv=value, k=1, hnv=1, hxv=1, max=1, min=0)
            cmds.setAttr("{0}Shape.{1}[{2}]."\
                         "{1}_Position".format(hairSys, scale_attribute, count),
                         position)
            cmds.connectAttr("{0}.{1}".format(dyCtrl, attribute),
                             "{0}Shape.{1}[{2}]."\
                             "{1}_FloatValue".format(hairSys, scale_attribute,
                                                     count))
            cmds.setAttr("{0}Shape.{1}[{2}]."\
                         "{1}_Interp".format(hairSys, scale_attribute, count),3)
        # last position
        last_pos = len(positions)
        long_name = "{0}{1}".format(end_name, "End")
        cmds.addAttr(dyCtrl, ln=long_name, at="float", dv=0,
                     k=1, hnv=1, hxv=1, max=1, min=0)
        cmds.setAttr("{0}Shape.{1}[{2}]."\
                     "{1}_Position".format(hairSys,scale_attribute, last_pos),1)
        cmds.connectAttr("{0}.{1}".format(dyCtrl, long_name),
                         "{0}Shape.{1}[{2}]."\
                         "{1}_FloatValue".format(hairSys, scale_attribute,
                                                 last_pos))
        cmds.setAttr("{0}Shape.{1}[{2}]."\
                     "{1}_Interp".format(hairSys, scale_attribute, last_pos), 3)

    def _control_settings(self, dyCtrl, hairSys, fol):
        """
        Responsible for setting the control attributes.
        """
        # header
        cmds.addAttr(dyCtrl, ln="control",at="enum",
                     en="Settings:", k=True)
        cmds.setAttr("{0}.control".format(dyCtrl), l=True)

        # show/hide attributes
        self._display_attributes("locatorVis", self.fk_group, dyCtrl)
        # scale locators
        cmds.addAttr(dyCtrl, ln="locatorScale", at="float", dv=1, k=True)
        for control in self.fk_controls:
            for attr in LOCAL_SCALE_ATTRS:
                cmds.connectAttr("{0}.locatorScale".format(dyCtrl),
                                 "{0}Shape.{1}".format(control, attr))

        self._display_attributes("dynamicVis", self.dynamic_control, dyCtrl)
        # scale dynamic control
        cmds.addAttr(dyCtrl, ln="dynamicScale", at="float", dv=1, k=True)
        for attr in SCALE_ATTRS:
            cmds.connectAttr("{0}.dynamicScale".format(dyCtrl),
                             "{0}.{1}".format(dyCtrl, attr))

    def _display_attributes(self, attribute, group, control):
        """
        Set's the show and hide attributes for the dynamic and locator controls.
        """
        # show/hide controls
        cmds.addAttr(control, ln=attribute, at="long",
                     dv=1,min=0, max=1, k=True)

        # hide locators
        cmds.connectAttr("{0}.{1}".format(control, attribute),
                         "{0}.visibility".format(group))

    def distribute(self):
        """
        Distribute Function
        """
        pass

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

    def _build_joints(self, suffix):
        """
        Build joints.
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
        self._snap_control(self.dynamic_control, self.pos_group, target)
        cmds.parent(self.pos_group, self.root_group)

    def _snap_control(self, control, group, target):
        """
        Handles snapping controls.
        """
        snap_tuple = (control, group)
        # snap the control
        for obj in snap_tuple:
            tmp_constraint = cmds.parentConstraint(target, obj)
            cmds.delete(tmp_constraint)
        cmds.parent(control, group)
        cmds.makeIdentity(control, apply=True)
        cmds.DeleteHistory(control)

    def _finalize(self):
        """
        Finalize rig.
        """
        # connect
        cmds.parent(self.fk_group, self.pos_group)
        cmds.parentConstraint(self.fk_controls[0], self.dynamic_control)
        for item in (self.fk_group, self.dynamic_joints[0]):
            cmds.parentConstraint(self.parent_control, item, mo=True)
        for count, control in enumerate(self.controls):
            cmds.parentConstraint(self.dynamic_joints[count], control, mo=True)

        # connect motion path to prevent flipping
        cmds.select(cl=True)
        cmds.select(self.motion_parent)
        cmds.select(self.curve, add=True)
        cmds.pathAnimation(su=self.start_frame, eu=self.end_frame)

        # lock and hide attributes on dynamic control
        for attr in ATTRS:
            cmds.setAttr("{0}.{1}".format(self.dynamic_control, attr),
                         l=True, k=False, cb=False)

        # create metadata
        self._create_meta_data()

    def _create_meta_data(self):
        """
        Creates a network node to hold the meta data for the rig.
        """
        network_node = cmds.createNode("network")
        meta_node_name = self._get_unique_name("metaNode", "DyMETA")
        meta_node = cmds.rename(network_node, meta_node_name)
        data = {
                "rootGroup" : self.root_group,
                "rigName" : self.rig_name,
                "parentControl" : self.parent_control,
                "controls" : self.controls,
                "pointLock" : self.point_lock,
                "startFrame" : self.start_frame,
                "endFrame" : self.end_frame,
                "dynamicControl" : self.dynamic_control,
                "metaNode" : meta_node,
                "hairSystem" : self.hair_system}
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

    def properties_page(self):
        """
        Opens the doc page for 2016 hair properties.
        """
        url = "http://help.autodesk.com/view/MAYAUL/2016/ENU" +\
              "/index.html?contextId=NODES-HAIRSYSTEM"
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def confluence_page(self):
        """
        Opens Confluence page on overlap tool.
        """
        url = "https://confluence.reelfx.com/display/ANIM/Overlap+Tool"
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
