#!/usr/bin/python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    UI Class for the Overlap Tool

    This tool is for building an overlap rig on top of an FK rig.
    This tool will allow the animator to change the dynamics of the overlap
    rig as well as layer the FK controls on top. After the animation is
    satisfied, the animator may bake down the animation from the overlap
    rig to the original FK controls.

:use:
    from ani_tools.rmaya.overlap_tool import overlap_tool
    overlap_tool.main()

:see also:
    ani_tools/rmaya/overlap_tool.py

TODO:
    - Batch Build.
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
import os

# third party
from maya import cmds, mel
from PyQt4 import QtGui, QtCore

# internal
from ani_tools.rmaya import overlap_tool

# external
from pipe_api.rmaya import rnodes
from ui_lib.window import RMainWindow

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class OverlapToolUI(RMainWindow):

    PREF_NAME = 'overlap_tool_ui'

    def __init__(self, *args, **kwargs):
        """
        The initializer.
        """
        # grab our api class
        self.overlap_obj = overlap_tool.OverlapTool()

        # super class
        RMainWindow.__init__(self, *args, **kwargs)

        # empty data
        self.controls = None
        self.point_lock = None
        self.frame_range = None
        self.parent_control = None

        # notification presets
        self.button = QtGui.QMessageBox.Ok
        self.title = "OOPS!"

        # build ui
        self.build_ui()

    def build_ui(self, *args):
        """
        Responsible for building the layout of the UI.
        """
        window_name = "Overlap Tool"

        # styling
        self._get_styling()

        # build main window
        self.setObjectName(window_name)
        self.setMinimumSize(300, 420)
        self.setMaximumSize(300, 420)
        self.setWindowTitle("Overlap Tool")

        # stay on top
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        # main widget
        main_widget = QtGui.QWidget()

        # main layout
        main_layout = QtGui.QVBoxLayout(main_widget)
        main_layout.setObjectName("main_layout")
        self.setCentralWidget(main_widget)

        # menu bar
        self.menu = QtGui.QMenuBar(self)
        self.menu.setStyleSheet(self.styling)
        self.setMenuBar(self.menu)

        # file
        self.file = self.menu.addMenu("File")

        # items
        self.save_menu_option = QtGui.QAction("Save", self.menu)
        self.save_menu_option.triggered.connect(self.overlap_obj._json_save)
        self.load_menu_option = QtGui.QAction("Load", self.menu)
        self.load_menu_option.triggered.connect(self.overlap_obj._json_load)
        self.file.addAction(self.save_menu_option)
        self.file.addAction(self.load_menu_option)

        # batch
        self.batch = self.menu.addMenu("Batch")

        # items
        # self.batch_build = QtGui.QAction("Build", self.menu)
        self.batch_bake = QtGui.QAction("Bake", self.menu)
        self.batch_delete = QtGui.QAction("Delete", self.menu)
        # self.batch.addAction(self.batch_build)
        self.batch.addAction(self.batch_bake)
        self.batch.addAction(self.batch_delete)

        # help
        self.help = self.menu.addMenu("Help")

        # items
        self.confluence_page = QtGui.QAction("Confluence Page", self.menu)
        self.properties_page = QtGui.QAction("Dynamic Hair Properties (2016)",
                                             self.menu)
        self.help.addAction(self.confluence_page)
        self.help.addAction(self.properties_page)

        # option layout
        option_layout = QtGui.QVBoxLayout()
        main_layout.addLayout(option_layout)

        assets_box_layout = QtGui.QHBoxLayout()
        option_layout.addLayout(assets_box_layout)

        presets_box_layout = QtGui.QHBoxLayout()
        option_layout.addLayout(presets_box_layout)

        assets_box_label = QtGui.QLabel("Asset:")
        assets_box_label.setMaximumWidth(35)
        assets_box = QtGui.QComboBox()
        # available assets
        for asset in rnodes.RAsset.iter_all():
            rasset = asset.get_path().split('|')[1]
            if ":" in rasset:
                rasset = rasset.split(':')[0]
            assets_box.addItem(rasset)
        assets_box_layout.addWidget(assets_box_label)
        assets_box_layout.addWidget(assets_box)

        # presets
        presets_box_label = QtGui.QLabel("Preset:")
        presets_box_label.setMaximumWidth(35)
        presets_box = QtGui.QComboBox()
        presets_box_layout.addWidget(presets_box_label)
        presets_box_layout.addWidget(presets_box)

        # preset buttons
        preset_button_layout = QtGui.QHBoxLayout()
        main_layout.addLayout(preset_button_layout)

        spacer = QtGui.QLabel(" ")
        spacer.setMaximumWidth(130)
        spacer.setMinimumWidth(130)

        save_button = QtGui.QPushButton("Save")
        load_button = QtGui.QPushButton("Load")
        preset_button_layout.addWidget(spacer)
        preset_button_layout.addWidget(save_button)
        preset_button_layout.addWidget(load_button)

        # basic settings
        divider_layout = QtGui.QHBoxLayout()
        main_layout.addLayout(divider_layout)

        divider_label = QtGui.QLabel("Settings")
        divider_label.setAlignment(QtCore.Qt.AlignCenter)
        divider_label.setMinimumHeight(20)
        divider_left = QtGui.QFrame()
        divider_left.setFrameShape(QtGui.QFrame.HLine)
        divider_left.setFrameShadow(QtGui.QFrame.Sunken)
        divider_right = QtGui.QFrame()
        divider_right.setFrameShape(QtGui.QFrame.HLine)
        divider_right.setFrameShadow(QtGui.QFrame.Sunken)
        divider_layout.addWidget(divider_left)
        divider_layout.addWidget(divider_label)
        divider_layout.addWidget(divider_right)

        # rigs in scene
        rig_box_layout = QtGui.QHBoxLayout()
        main_layout.addLayout(rig_box_layout)

        rig_box_label = QtGui.QLabel("Rigs:")
        rig_box_label.setMaximumWidth(35)
        self.rig_box = QtGui.QComboBox()
        self.rig_box.setStyleSheet(self.styling)
        rigs = self._find_rigs()
        select_all_button = QtGui.QPushButton("Select All")
        select_all_button.setMaximumWidth(60)
        select_dynamic_control = QtGui.QPushButton("Select")
        select_dynamic_control.setMaximumWidth(60)
        for rig in rigs:
            rig = rig.split("_dynamic")[0]
            rig = rig.split("|")[1]
            self.rig_box.addItem(rig)
        rig_box_layout.addWidget(rig_box_label)
        rig_box_layout.addWidget(self.rig_box)
        rig_box_layout.addWidget(select_all_button)
        rig_box_layout.addWidget(select_dynamic_control)

        # rig name
        rig_name_layout = QtGui.QHBoxLayout()
        main_layout.addLayout(rig_name_layout)

        rig_name_label = QtGui.QLabel("Name:  ")
        self.rig_name_input_box = QtGui.QLineEdit()
        self.rig_name_input_box.setPlaceholderText("Give your rig a name")
        rig_name_layout.addWidget(rig_name_label)
        rig_name_layout.addWidget(self.rig_name_input_box)

        # parent
        parent_layout = QtGui.QHBoxLayout()
        main_layout.addLayout(parent_layout)

        parent_label = QtGui.QLabel("Parent: ")
        self.parent_input_box = QtGui.QLineEdit()
        self.parent_input_box.setPlaceholderText("Select a parent control")
        set_button = QtGui.QPushButton("Set")
        set_button.setMinimumWidth(60)
        parent_layout.addWidget(parent_label)
        parent_layout.addWidget(self.parent_input_box)
        parent_layout.addWidget(set_button)

        # frame label
        frame_range_label_layout = QtGui.QHBoxLayout()
        main_layout.addLayout(frame_range_label_layout)

        start_frame_label = QtGui.QLabel(" Start:            End:")
        frame_range_label_layout.addWidget(start_frame_label)

        # frame range
        frame_range_layout = QtGui.QHBoxLayout()
        main_layout.addLayout(frame_range_layout)

        self.start_frame = cmds.playbackOptions(q=True, min=True)
        self.end_frame = cmds.playbackOptions(q=True, max=True)

        self.start_frame_box = QtGui.QSpinBox()
        self.start_frame_box.setMaximumWidth(70)
        self.start_frame_box.setMaximum(1000)
        self.start_frame_box.setValue(self.start_frame)
        self.end_frame_box = QtGui.QSpinBox()
        self.end_frame_box.setMaximum(1000)
        self.end_frame_box.setValue(self.end_frame)
        self.end_frame_box.setMaximumWidth(70)
        point_lock_options = ('Base', 'Both Ends')
        point_lock_label = QtGui.QLabel("Attached At: ")
        self.point_lock_option = QtGui.QComboBox()
        for option in point_lock_options:
            self.point_lock_option.addItem(option)
        frame_range_layout.addWidget(self.start_frame_box)
        frame_range_layout.addWidget(self.end_frame_box)
        frame_range_layout.addWidget(point_lock_label)
        frame_range_layout.addWidget(self.point_lock_option)

        # build layout
        build_layout = QtGui.QHBoxLayout()
        main_layout.addLayout(build_layout)

        build_button = QtGui.QPushButton("Build")
        build_button.setStyleSheet("background-color: green;")
        bake_button = QtGui.QPushButton("Bake")
        bake_button.setStyleSheet("background-color: yellow; color: black;")
        delete_button = QtGui.QPushButton("Delete")
        delete_button.setStyleSheet("background-color: red;")
        build_layout.addWidget(build_button)
        build_layout.addWidget(bake_button)
        build_layout.addWidget(delete_button)

        # control settings
        control_options_layout = QtGui.QHBoxLayout()
        main_layout.addLayout(control_options_layout)

        control_options_label = QtGui.QLabel("Control")
        control_options_label.setAlignment(QtCore.Qt.AlignCenter)
        control_options_label.setMinimumHeight(20)
        divider_left = QtGui.QFrame()
        divider_left.setFrameShape(QtGui.QFrame.HLine)
        divider_left.setFrameShadow(QtGui.QFrame.Sunken)
        divider_right = QtGui.QFrame()
        divider_right.setFrameShape(QtGui.QFrame.HLine)
        divider_right.setFrameShadow(QtGui.QFrame.Sunken)
        control_options_layout.addWidget(divider_left)
        control_options_layout.addWidget(control_options_label)
        control_options_layout.addWidget(divider_right)

        # distribute
        distribute_layout = QtGui.QHBoxLayout()
        distribute_layout.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignLeft)
        main_layout.addLayout(distribute_layout)

        distribute_button = QtGui.QPushButton("Distribute")
        distribute_button.setMaximumWidth(100)
        self.distribute_options_menu = QtGui.QComboBox()
        self.distribute_options_menu.setMaximumWidth(100)
        for option in ["Ease In", "Ease Out", "Linear"]:
            self.distribute_options_menu.addItem(option)
        stiffness_ramp = QtGui.QPushButton("Stiffness")
        attraction_ramp = QtGui.QPushButton("Attraction")

        distribute_layout.addWidget(distribute_button)
        distribute_layout.addWidget(self.distribute_options_menu)
        distribute_layout.addWidget(stiffness_ramp)
        distribute_layout.addWidget(attraction_ramp)

        # play layout
        play_layout = QtGui.QHBoxLayout()
        main_layout.addLayout(play_layout)

        self.reset_button = QtGui.QPushButton("|<<")
        self.reset_button.setMaximumWidth(30)
        self.play_button = QtGui.QPushButton("PLAY")
        play_layout.addWidget(self.reset_button)
        play_layout.addWidget(self.play_button)

        # signals
        build_button.clicked.connect(self._build)
        delete_button.clicked.connect(self._delete)
        self.play_button.clicked.connect(self._play)
        self.reset_button.clicked.connect(self._reset)
        bake_button.clicked.connect(self._bake)
        set_button.clicked.connect(self._set_parent_control)
        save_button.clicked.connect(self._save)
        load_button.clicked.connect(self._load)
        self.rig_box.activated.connect(self._select_dynamic_control)
        select_dynamic_control.clicked.connect(self._select_dynamic_control)
        select_all_button.clicked.connect(self._select_all_dynamic_controls)
        self.batch_bake.triggered.connect(self._batch_bake)
        self.batch_delete.triggered.connect(self._batch_delete)
        self.confluence_page.triggered.connect(self.overlap_obj.confluence_page)
        self.properties_page.triggered.connect(self.overlap_obj.properties_page)
        stiffness_ramp.clicked.connect(self._stiffness_ramp)
        attraction_ramp.clicked.connect(self._attraction_ramp)

    def _get_styling(self):
        """
        Sets the main styling.
        """
        self.styling = """
              QMenu {
                  text-align: left;
                  background-color: #444444;
                  border: 1px solid grey;
              }

              QMenu::item::selected {
                  background-color: #4c7380;
              }

              QMenuBar::item::selected {
                  background-color: #4c7380;
              }

              QComboBox::item {
                  height: 30px;
              }"""

    def _set_parent_control(self):
        """
        Sets the parent control that the dynamic rig will use to be driven by.
        """
        selection = cmds.ls(sl=True)
        if not selection:
            msg = "Please select a Parent Control."
            error = QtGui.QMessageBox.information(self, self.title,
                                               msg, self.button)
            return

        self.parent_input_box.setText(str(selection[0]))
        self.parent_control = str(self.parent_input_box.text())

    def _build(self):
        """
        Builds the Dynamic Rig.
        """
        # gather overlap data
        self.rig_name = str(self.rig_name_input_box.text())
        self.controls = cmds.ls(sl=True)
        self.point_lock = self.point_lock_option.currentIndex()
        start = self.start_frame_box.value()
        end = self.end_frame_box.value()
        self.frame_range = (start, end)

        # input checks
        if not self.rig_name:
            msg = "Please give your rig a name."
            error = QtGui.QMessageBox.information(self, self.title,
                                               msg, self.button)
            return
        if not self.parent_control:
            msg = "Please select a Parent Control."
            error = QtGui.QMessageBox.information(self, self.title,
                                               msg, self.button)
            return
        if len(self.controls) <= 1:
            msg = "Please select more than one FK control."
            error = QtGui.QMessageBox.information(self, self.title,
                                               msg, self.button)
            return
        if self.end_frame == 0:
            msg = "Please choose a frame range."
            error = QtGui.QMessageBox.information(self, self.title,
                                               msg, self.button)
            return

        # build
        self.overlap_obj.build(self.rig_name, self.parent_control,
                           self.controls, self.point_lock, self.frame_range)

        rigs = self._find_rigs()
        rigs.reverse()
        for rig in rigs:
            rig = rig.split("_dynamic")[0]
            rig = rig.split("|")[1]
            rig_exists = self.rig_box.findText(rig, QtCore.Qt.MatchFixedString)
            if not rig_exists >= 0:
                self.rig_box.addItem(rig)
                index = self.rig_box.findText(rig)
                self.rig_box.setCurrentIndex(index)

        # select dynamic control
        self._select_dynamic_control()

    def _find_rigs(self):
        """
        Finds all Dynamic rigs in the scene.
        """
        rigs = list()
        transforms = cmds.ls(type="transform", l=True)
        for transform in transforms:
            if transform.endswith("_DyROOT"):
                rigs.append(transform)
        return rigs

    def _delete(self):
        """
        Deletes any dynamic rig in the scene.
        """
        # clear widgets
        self._clear(self.parent_input_box)
        self._clear(self.rig_name_input_box)

        # check for rigs
        self._rig_check()

        # find rigs
        rig_to_delete = None
        rigs = self.overlap_obj.find_meta_attribute("rootGroup")
        for rig in rigs:
            rig_base_name = rig.split("_dynamic")[0]
            if rig_base_name == self.rig_box.currentText():
                rig_to_delete = rig

        # delete rig
        self.overlap_obj.delete(rig_to_delete)

        # clear rigs
        self.rig_box.removeItem(self.rig_box.currentIndex())

    def _batch_delete(self):
        """
        Deletes all overlap rigs in the scene.
        """
        # delete rigs
        self._rig_check()
        self.overlap_obj.batch_delete()

        # clear all widgets
        widgets = [self.parent_input_box, self.rig_name_input_box, self.rig_box]
        for widget in widgets:
            self._clear(widget)

    def _bake(self):
        """
        Handles baking out the animation
        """
        start = self.start_frame_box.value()
        end = self.end_frame_box.value()
        frame_range = (start, end)
        controls = self.controls
        if self.rig_box.currentText() and not frame_range:
            controls = cmds.ls(sl=True)
            if not controls:
                    msg = "Please Select Controls to bake"
                    QtGui.QMessageBox.information(self, self.title,
                                                   msg, self.button)
                    return
            start = self.start_frame_box.value()
            end = self.end_frame_box.value()
            frame_range = (start, end)

        elif not self.rig_box.currentText():
            msg = "Please 'Build' your rig first."
            error = QtGui.QMessageBox.information(self, self.title,
                                               msg, self.button)
            return

        # bake animation
        bake_animation = self.overlap_obj.bake(controls, frame_range)

    def _batch_bake(self):
        """
        Bakes out all rigs in the scene.
        """
        self._rig_check()
        start = self.start_frame_box.value()
        end = self.end_frame_box.value()
        frame_range = (start, end)

        self.overlap_obj.batch_bake(frame_range)

    def _play(self):
        """
        Responsible for interactive playback.
        """
        if self.play_button.text() == "PLAY":
            self.play_button.setText("STOP")
            self.play_button.setStyleSheet("background-color: red;")
            cmds.InteractivePlayback()
        elif self.play_button.text() == "STOP":
            self.play_button.setStyleSheet("background-color: light gray;")
            self.play_button.setText("PLAY")
            cmds.play(state=False)

    def _reset(self):
        """
        Resets the timeline for playback.
        """
        cmds.currentTime(self.start_frame)

    def _select_dynamic_control(self):
        """
        Selects the dynamic control.
        """
        self._rig_check()
        controls = self.overlap_obj.find_meta_attribute("dynamicControl")
        for control in controls:
            if control.startswith(self.rig_box.currentText() + "_"):
                    cmds.select(control, r=True)

    def _select_all_dynamic_controls(self):
        """
        Selects all dynamic controls in the scene.
        """
        self._rig_check()
        controls = self.overlap_obj.find_meta_attribute("dynamicControl")
        cmds.select(controls, r=True)

    def _attraction_ramp(self):
        """
        Opens Attraction Ramp.
        """
        self._rig_check()
        hair_systems = self.overlap_obj.find_meta_attribute("hairSystem")
        for system in hair_systems:
            if system.startswith(self.rig_box.currentText()):
                ramp = "editRampAttribute " + system + "Shape.attractionScale"
                mel.eval(ramp)

    def _stiffness_ramp(self):
        """
        Opens Stiffness Ramp.
        """
        self._rig_check()
        hair_systems = self.overlap_obj.find_meta_attribute("hairSystem")
        for system in hair_systems:
            if system.startswith(self.rig_box.currentText()):
                ramp = "editRampAttribute " + system + "Shape.stiffnessScale"
                mel.eval(ramp)

    def _data(self, mode="save"):
        """
        Handles gathering all of the needed overlap data.
        @param:
            mode: Can either be "save" or "load".
        """
        overlap_data = dict()
        dy_attrs = dict()
        if mode == "save":
            current_rig = self.rig_box.currentText()
            meta_nodes = self.overlap_obj.find_meta_attribute("metaNode")
            controls = self.overlap_obj.find_meta_attribute("dynamicControl")
            meta_node = None
            for node in meta_nodes:
                if node.startswith(current_rig):
                    meta_node = node
            if meta_node:
                # data
                attributes = cmds.listAttr(meta_node, ud=True)
                for attribute in attributes:
                    value = cmds.getAttr("{0}.{1}".format(meta_node, attribute))
                    overlap_data[attribute] = value
                # attributes
                for control in controls:
                    if control.startswith(current_rig):
                        attributes = cmds.listAttr(control, ud=True)
                        for attribute in attributes:
                            value = cmds.getAttr("{0}.{1}".format(control,
                                                                  attribute))
                            dy_attrs[attribute] = value
                        overlap_data["dynamicAttributes"] = dy_attrs
                path = self.overlap_obj._json_save(overlap_data)
                return path
            return overlap_data
        elif mode == "load":
            # data
            self.overlap_data = self.overlap_obj._json_load()

            # cancel
            if not self.overlap_data:
                return
            # new loaded data
            self.root_group = self.overlap_data["rootGroup"]
            self.rig_name = self.overlap_data["rigName"]
            self.parent_control = self.overlap_data["parentControl"]
            self.controls = self.overlap_data["controls"]
            self.point_lock = int(self.overlap_data["pointLock"])
            self.start_frame = int(self.overlap_data["startFrame"])
            self.end_frame = int(self.overlap_data["endFrame"])
            self.dynamic_control = self.overlap_data["dynamicControl"]

    def _save(self):
        """
        Handles Saving.
        """
        path = self._data("save")
        if not path:
            msg = "Please Build a Rig before trying to save."
            info = QtGui.QMessageBox.information(self, "Success",
                                                 msg, self.button)
            return
        elif os.path.isfile(path):
            msg = "Data successfully saved to: {0}".format(path)
            info = QtGui.QMessageBox.information(self, "Success",
                                                 msg, self.button)

    def _load(self):
        """
        Handles Loading.
        """
        self._data("load")
        if not self.overlap_data:
            return

        msg = "Your data has successfully been loaded, please press 'Build'."
        build_button = QtGui.QPushButton("Build")
        warning = QtGui.QMessageBox()
        warning.setText(msg)
        warning.addButton(QtGui.QPushButton("Build"), QtGui.QMessageBox.YesRole)
        warning.addButton(QtGui.QPushButton("Cancel"), QtGui.QMessageBox.NoRole)
        build = warning.exec_()
        if build == 1:
            return

        # populate
        self.rig_box.addItem(self.rig_name)
        index = self.rig_box.findText(self.rig_name)
        self.rig_box.setCurrentIndex(index)
        self.rig_name_input_box.setText(self.rig_name)
        self.parent_input_box.setText(self.parent_control)
        for control in self.controls:
            cmds.select(control, add=True)
        self.point_lock_option.setCurrentIndex(self.point_lock)
        self.start_frame_box.setValue(self.start_frame)
        self.end_frame_box.setValue(self.end_frame)

        # build
        self._build()

        # set dynamic control attributes
        dy_attrs = self.overlap_data["dynamicAttributes"]
        for key, value in dy_attrs.iteritems():
            state = cmds.getAttr("{0}.{1}".format(self.dynamic_control, key),
                                                  l=True)
            if state:
                continue
            cmds.setAttr("{0}.{1}".format(self.dynamic_control, key), value)

    def _rig_check(self):
        """
        Checks for existing rigs.
        """
        current_rig = self.rig_box.currentText()
        if not current_rig:
            msg = "No Dynamic Rig found."
            error = QtGui.QMessageBox.information(self, self.title,
                                                  msg, self.button)
            return

    def _clear(self, widget):
        """
        Clear items in widget area.
        """
        widget.clear()

def main():
    OverlapToolUI.singleton().start()

if __name__ == "__main__":
    main()
