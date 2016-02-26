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

TODO:
    - Batch Bake.
    - Batch Build.
    - Individual attributes for dynamic FK controls (curve attract).
    - Global Save and Load settings.
    - Part naming for multiple dynamic rigs in the scene.
    - Delete individual rigs, not just all.

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
from maya import cmds, mel

# third party
from PyQt4 import QtGui, QtCore

# internal
from ani_tools.rmaya import overlap_tool

# external
from pipe_api.rmaya import rnodes
from ui_lib.window import RWindow

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class OverlapToolUI(RWindow):

    PREF_NAME = 'overlap_tool_ui'

    def __init__(self, *args, **kwargs):
        """
        The initializer.
        """
        # grab our api class
        self.overlap_obj = overlap_tool.OverlapTool()

        # super class
        RWindow.__init__(self, *args, **kwargs)

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

        # build main window
        self.setObjectName(window_name)
        self.setMinimumSize(300, 420)
        self.setMaximumSize(300, 420)
        self.setWindowTitle("Overlap Tool")

        # stay on top
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        # main layout
        main_layout = QtGui.QVBoxLayout()
        main_layout.setObjectName("main_layout")
        self.setLayout(main_layout)

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
        spacer.setMaximumWidth(100)
        spacer.setMinimumWidth(100)

        save_button = QtGui.QPushButton("Save")
        load_button = QtGui.QPushButton("Load")
        load_all_button = QtGui.QPushButton("Build All")
        preset_button_layout.addWidget(spacer)
        preset_button_layout.addWidget(save_button)
        preset_button_layout.addWidget(load_button)
        preset_button_layout.addWidget(load_all_button)

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

        # rig in scene
        rig_box_layout = QtGui.QHBoxLayout()
        main_layout.addLayout(rig_box_layout)

        rig_box_label = QtGui.QLabel("Rigs:")
        rig_box_label.setMaximumWidth(35)
        self.rig_box = QtGui.QComboBox()
        rigs = self._find_rigs()
        for rig in rigs:
            rig = rig.split("_dynamic")[0]
            rig = rig.split("|")[1]
            self.rig_box.addItem(rig)
        rig_box_layout.addWidget(rig_box_label)
        rig_box_layout.addWidget(self.rig_box)

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
        select_button = QtGui.QPushButton("Select")
        select_button.setMinimumWidth(60)
        parent_layout.addWidget(parent_label)
        parent_layout.addWidget(self.parent_input_box)
        parent_layout.addWidget(select_button)

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
        self.start_frame_box.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.end_frame_box = QtGui.QSpinBox()
        self.end_frame_box.setMaximum(1000)
        self.end_frame_box.setValue(self.end_frame)
        self.end_frame_box.setMaximumWidth(70)
        self.end_frame_box.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        point_lock_options = ('Base', 'Both Ends')
        point_lock_label = QtGui.QLabel("Attached At: ")
        point_lock_label.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.point_lock_option = QtGui.QComboBox()
        for option in point_lock_options:
            self.point_lock_option.addItem(option)
        frame_range_layout.addWidget(self.start_frame_box)
        frame_range_layout.addWidget(self.end_frame_box)
        frame_range_layout.addWidget(point_lock_label)
        frame_range_layout.addWidget(self.point_lock_option)

        # selection layout
        selection_layout = QtGui.QHBoxLayout()
        selection_label_layout = QtGui.QHBoxLayout()
        selected_controls_label = QtGui.QLabel("Controls:")
        self.hide_controls_button = QtGui.QPushButton("Hide Controls")
        select_dynamic_control = QtGui.QPushButton("Select Dynamic Control")
        selection_label_layout.addWidget(selected_controls_label)
        selection_label_layout.addWidget(self.hide_controls_button)
        selection_label_layout.addWidget(select_dynamic_control)
        main_layout.addLayout(selection_label_layout)
        main_layout.addLayout(selection_layout)

        self.selected_controls = QtGui.QListWidget()
        self.selected_controls.setMaximumSize(350, 50)
        selection_layout.addWidget(self.selected_controls)

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
        select_button.clicked.connect(self._set_parent_control)
        self.hide_controls_button.clicked.connect(self._hide_controls)
        select_dynamic_control.clicked.connect(self._select_dynamic_control)
        save_button.clicked.connect(self._save)
        load_button.clicked.connect(self._load)

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
        # clear widgets
        self._clear(self.selected_controls)

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

        # populate
        for control in self.controls:
            control = QtGui.QListWidgetItem(control)
            self.selected_controls.addItem(control)
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
        Deletes any dynamic rigs in the scene.
        """
        # clear widgets
        self._clear(self.selected_controls)
        self._clear(self.parent_input_box)
        self._clear(self.rig_name_input_box)

        # check for rigs
        current_rig = self.rig_box.currentText()
        if not current_rig:
            msg = "No Dynamic Rig found."
            error = QtGui.QMessageBox.information(self, self.title,
                                                  msg, self.button)
            return

        # find rigs
        rigs = self._find_rigs()
        rig_to_delete = None
        for rig in rigs:
            rig_base_name = rig.split("_dynamic")[0]
            rig_base_name = rig_base_name.split("|")[1]
            if rig_base_name == self.rig_box.currentText():
                rig_to_delete = rig

        # delete rig
        self.overlap_obj.delete(rig_to_delete)

        # clear rigs
        self.rig_box.removeItem(self.rig_box.currentIndex())

    def _bake(self):
        """
        Handles baking out the animation
        TODO:
            Baking even after you close the overlap tool (meta data node).
        """
        frame_range = self.frame_range
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

    def _hide_controls(self):
        """
        Responsible for hiding and showing controls.
        """
        rigs = self._find_rigs()
        relatives = list()
        if self.hide_controls_button.text() == "Hide Controls":
            self.hide_controls_button.setText("Show Controls")
            for rig in rigs:
                rig_base_name = rig.split("_dynamic")[0]
                rig_base_name = rig_base_name.split("|")[1]
                if rig_base_name == self.rig_box.currentText():
                    relatives = cmds.listRelatives(rig, ad=True)
            for child in relatives:
                if child.endswith("DyFKCtrl"):
                    cmds.setAttr("{0}Shape.visibility".format(child), 0)
                if child.endswith("DyCtrl"):
                    cmds.setAttr("{0}Shape.visibility".format(child), 0)
        elif self.hide_controls_button.text() == "Show Controls":
            self.hide_controls_button.setText("Hide Controls")
            for rig in rigs:
                rig_base_name = rig.split("_dynamic")[0]
                rig_base_name = rig_base_name.split("|")[1]
                if rig_base_name == self.rig_box.currentText():
                    relatives = cmds.listRelatives(rig, ad=True)
            for child in relatives:
                if child.endswith("DyFKCtrl"):
                    cmds.setAttr("{0}Shape.visibility".format(child), 1)
                if child.endswith("DyCtrl"):
                    cmds.setAttr("{0}Shape.visibility".format(child), 1)

    def _select_dynamic_control(self):
        """
        Selects the dynamic control.
        """
        rigs = self._find_rigs()
        for rig in rigs:
            rig_base_name = rig.split("_dynamic")[0]
            rig_base_name = rig_base_name.split("|")[1]
            if rig_base_name == self.rig_box.currentText():
                relatives = cmds.listRelatives(rig, ad=True)
                for child in relatives:
                    if child.endswith("DyCtrl"):
                        cmds.select(child)

        if not rigs:
            msg = "No Dynamic Control found."
            error = QtGui.QMessageBox.information(self, self.title,
                                               msg, self.button)
            return

    def _data(self, mode="save"):
        """
        Handles gathering all of the needed overlap data.
        @param:
            mode: Can either be "save" or "load".
        """
        overlap_data = dict()
        if mode == "save":
            if self.parent_control:
                overlap_data["rig_name"] = self.rig_name
                overlap_data["parent_control"] = self.parent_control
                overlap_data["selection"] = self.controls
                overlap_data["point_lock"] = self.point_lock
                overlap_data["frame_range"] = (self.start_frame, self.end_frame)
                path = self.overlap_obj._json_save(overlap_data)
                return path
            else:
                return overlap_data
        elif mode == "load":
            # data
            self.overlap_data = self.overlap_obj._json_load()

            # cancel
            if not self.overlap_data:
                return
            self.rig_name = self.overlap_data["rig_name"]
            self.parent_control = self.overlap_data["parent_control"]
            self.controls = self.overlap_data["selection"]
            self.point_lock = self.overlap_data["point_lock"]
            self.start_frame, self.end_frame = self.overlap_data["frame_range"]

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
        info = QtGui.QMessageBox.information(self, "Success",
                                          msg, self.button)

        # populate
        self.rig_box.addItem(self.rig_name)
        self.rig_name_input_box.setText(self.rig_name)
        self.parent_input_box.setText(self.parent_control)
        for control in self.controls:
            cmds.select(control, add=True)
            control = QtGui.QListWidgetItem(control)
            self.selected_controls.addItem(control)
        self.point_lock_option.setCurrentIndex(self.overlap_data["point_lock"])
        self.start_frame_box.setValue(self.start_frame)
        self.end_frame_box.setValue(self.end_frame)

    def _clear(self, widget):
        """
        Clear items in widget area.
        """
        widget.clear()

def main():
    OverlapToolUI.singleton().start()

if __name__ == "__main__":
    main()
