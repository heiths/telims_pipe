#!/usr/bin/python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    package builder for zipping or copying different directory structures.

:to use:
    python package_builder.py
"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
import os, sys, shutil, errno, json
from zipfile import ZipFile, ZIP_DEFLATED

# third-party
from PySide import QtGui, QtCore

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- GLOBALS --#

SCRIPTS_PATH = "D:/Build/usr/jeremy_ernst/MayaTools"

#------------------------------------------------------------------------------#
#--------------------------------------------------------------------- UTILS --#

def convert_path(path):
    """Converts to Windows readable path"""
    separator = os.sep
    if separator != "/":
        path = path.replace(os.sep, "/")
    return path

def build_path(folder, name):
    return convert_path(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                     folder, name))

def divider_label(layout, label):
    """
    Creates a centered label header.
    """
    # attach to layout
    divider_layout = QtGui.QHBoxLayout()
    layout.addLayout(divider_layout)

    # define divider
    divider_label = QtGui.QLabel(label)
    divider_label.setAlignment(QtCore.Qt.AlignCenter)
    divider_label.setMinimumHeight(20)
    divider_left = QtGui.QFrame()
    divider_left.setStyleSheet("border: 2px solid #2c2d2f;")
    divider_left.setFrameShape(QtGui.QFrame.HLine)
    divider_left.setFrameShadow(QtGui.QFrame.Sunken)
    divider_right = QtGui.QFrame()
    divider_right.setStyleSheet("border: 2px solid #2c2d2f;")
    divider_right.setFrameShape(QtGui.QFrame.HLine)
    divider_right.setFrameShadow(QtGui.QFrame.Sunken)
    divider_layout.addWidget(divider_left)
    divider_layout.addWidget(divider_label)
    divider_layout.addWidget(divider_right)

def update_line_edit(line_edit_widget):
    """Finds path and populates QLineEdit"""
    path = QtGui.QFileDialog.getExistingDirectory()
    if path:
        return line_edit_widget.setText(path)

def json_save(data=None, path=None):
    """Saves out given data into a json file."""
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

def json_load(path=None):
    """This procedure loads and returns the content of a json file."""
    if not path:
        path = cmds.fileDialog2(fm=1, ds=2, ff="*.json")
        if not path:
            return
        path = path[0]

    fobj = open(path)
    data = json.load(fobj)
    return data

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class PackageBuilder(QtGui.QWidget):
    def __init__(self):
        super(PackageBuilder, self).__init__()

        # globals
        self._build_launcher()

    def _build_launcher(self):

        # set styling
        style_sheet_file = QtCore.QFile(build_path('stylesheets', 'aaron_dark.qss'))
        style_sheet_file.open(QtCore.QFile.ReadOnly)
        self.setStyleSheet(str(style_sheet_file.readAll()))

        # define window
        self.setWindowTitle("Package Builder")
        self.setObjectName("PackageBuilder")
        self.setMinimumHeight(700)
        self.setMaximumWidth(450)
        self.setMinimumWidth(450)

        # main layout
        self.main_layout = QtGui.QVBoxLayout(self)

        # header
        label = QtGui.QLabel()
        header_path = build_path('images', 'package_builder_banner.jpg')
        pixmap = QtGui.QPixmap(header_path)
        label.setPixmap(pixmap)

        header_layout = QtGui.QVBoxLayout()
        self.main_layout.addLayout(header_layout)
        header_layout.addWidget(label)

        # root directory
        root_directory_layout = QtGui.QHBoxLayout()
        self.main_layout.addLayout(root_directory_layout)

        root_label = QtGui.QLabel("Root Directory: ")
        self.root_directory = QtGui.QLineEdit()
        self.root_directory.setText(SCRIPTS_PATH)
        browse_button = QtGui.QPushButton("...")
        browse_button.setObjectName('roundedButton')
        root_directory_layout.addWidget(root_label)
        root_directory_layout.addWidget(self.root_directory)
        root_directory_layout.addWidget(browse_button)

        # body
        body_layout = QtGui.QHBoxLayout()
        self.main_layout.addLayout(body_layout)

        # template area
        package_template_layout = QtGui.QVBoxLayout()
        body_layout.addLayout(package_template_layout)

        # build label
        label_layout = QtGui.QVBoxLayout()
        package_template_layout.addLayout(label_layout)
        divider_label(label_layout, "BUILDS")

        # scroll area
        scroll_area = QtGui.QScrollArea()
        scroll_area.setStyleSheet("background-color: #2c2d2f;")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFocusPolicy(QtCore.Qt.NoFocus)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        package_template_layout.addWidget(scroll_area)

        scroll_widget = QtGui.QWidget()
        scroll_layout = QtGui.QVBoxLayout()
        scroll_layout.setAlignment(QtCore.Qt.AlignTop)
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)

        # package templates
        self.package_builder_layout = QtGui.QVBoxLayout()
        self.package_builder_layout.setContentsMargins(0,0,0,0)
        self.package_builder_layout.setSpacing(0)
        scroll_layout.addLayout(self.package_builder_layout)

        # build
        template_button_layout = QtGui.QHBoxLayout()
        package_template_layout.addLayout(template_button_layout)
        new_package_template_button = QtGui.QPushButton("NEW Package Template")
        new_package_template_button.setMaximumWidth(200)
        self.notification = QtGui.QLabel()
        self.notification.setStyleSheet("color : rgb(0, 255, 0);")
        template_button_layout.addWidget(new_package_template_button)
        template_button_layout.addWidget(self.notification, 0, QtCore.Qt.AlignRight)

        # signals
        new_package_template_button.clicked.connect(self._add)
        browse_button.clicked.connect(lambda: update_line_edit(self.root_directory))

        self.show()

    def _add(self):
        # clear notifications
        self.notification.clear()

        root_directory = convert_path(self.root_directory.text())
        if not os.path.isdir(root_directory):
            notice = "Please provide a root directory on disk..."
            return self.notification.setText(notice)
        new_widget = PackageBuilderWidget(root_directory,
                                          self.notification)
        self.package_builder_layout.addWidget(new_widget)

    def _select_item(self, selected_item=None):
        if not selected_item:
            selected_item = self.package_tree.currentItem()
        selected_item.setSelected(True)
        for i in xrange(selected_item.childCount()):
            child = selected_item.child(i)
            self._select_item(child)


class PackageBuilderWidget(QtGui.QFrame):
    def __init__(self, root_directory, notification):
        super(PackageBuilderWidget, self).__init__()
        self.root_directory = root_directory
        self.package_container = dict()
        self.notification = notification
        self.package_paths = list()

        # styling
        style_sheet_file = QtCore.QFile(build_path('stylesheets', 'aaron_dark.qss'))
        style_sheet_file.open(QtCore.QFile.ReadOnly)
        self.setStyleSheet(str(style_sheet_file.readAll()))
        self.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)

        self.setLayout(QtGui.QVBoxLayout())
        self.setObjectName('background')
        self.layout().setContentsMargins(3,1,3,3)
        self.layout().setSpacing(0)

        # main widget
        main_widget = QtGui.QWidget()
        main_widget.setLayout(QtGui.QVBoxLayout())
        main_widget.layout().setContentsMargins(2,2,2,2)
        main_widget.layout().setSpacing(5)
        main_widget.setFixedWidth(400)
        self.layout().addWidget(main_widget)

        # layouts
        close_layout  = QtGui.QHBoxLayout()
        name_layout  = QtGui.QHBoxLayout()
        preset_layout = QtGui.QHBoxLayout()
        package_layout = QtGui.QHBoxLayout()
        edit_items_layout = QtGui.QHBoxLayout()
        divider_layout = QtGui.QHBoxLayout()
        password_layout = QtGui.QHBoxLayout()
        out_path_layout = QtGui.QHBoxLayout()
        build_layout  = QtGui.QHBoxLayout()
        main_widget.layout().addLayout(close_layout)
        main_widget.layout().addLayout(name_layout)
        main_widget.layout().addLayout(preset_layout)
        main_widget.layout().addLayout(package_layout)
        main_widget.layout().addLayout(edit_items_layout)
        main_widget.layout().addLayout(divider_layout)
        main_widget.layout().addLayout(password_layout)
        main_widget.layout().addLayout(out_path_layout)
        main_widget.layout().addLayout(build_layout)

        # close button
        self.close_button = QtGui.QPushButton('X')
        self.close_button.setMinimumWidth(95)
        self.close_button.setObjectName('roundedButton')
        close_layout.addWidget(self.close_button, 0, QtCore.Qt.AlignRight)

        # naming
        name_label = QtGui.QLabel("Name: ")
        name_label.setMaximumWidth(50)
        self.name_line = QtGui.QLineEdit()
        self.name_line.setMaximumWidth(190)
        self.name_line.setPlaceholderText("Untitled")
        format_label = QtGui.QLabel("Format: ")
        format_label.setMaximumWidth(50)
        self.format = QtGui.QComboBox()
        self.format.setEditable(True)
        self.format.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
        for option in ["zip", "-- None --"]:
            self.format.addItem(option)
        self.format.setCurrentIndex(1)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_line)
        name_layout.addWidget(format_label)
        name_layout.addWidget(self.format)

        # presets
        preset_label = QtGui.QLabel("Presets: ")
        preset_label.setMaximumWidth(50)
        self.presets = QtGui.QComboBox()
        self.presets.addItem("-- None --")
        self.presets.setCurrentIndex(0)

        # populate presets
        self._populate_presets()

        save_button = QtGui.QPushButton("Save")
        save_button.setMaximumWidth(70)
        save_button.setObjectName('roundedButton')
        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.presets)
        preset_layout.addWidget(save_button)

        # packages
        self.packages = QtGui.QTreeWidget()
        self.packages.setMinimumHeight(200)
        header = QtGui.QTreeWidgetItem(["PACKAGES:"])
        self.packages.setHeaderItem(header)
        self.packages.setSelectionMode(QtGui.QTreeWidget.ContiguousSelection)
        package_layout.addWidget(self.packages)

        # populate packages
        self.populate_packages()

        # edit items
        delete_button = QtGui.QPushButton("delete")
        delete_button.setMaximumWidth(100)
        edit_items_layout.addWidget(delete_button, 0, QtCore.Qt.AlignRight)

        # divider
        divider_label(divider_layout, "Export")

        # password
        self.password_checkbox = QtGui.QCheckBox("Password")
        self.password_checkbox.setChecked(False)
        self.password = QtGui.QLineEdit()
        self.password.setPlaceholderText("123abc")
        self.password.setEnabled(False)
        password_layout.addWidget(self.password_checkbox)
        password_layout.addWidget(self.password)

        # out path
        out_path_label = QtGui.QLabel("Out Path: ")
        self.out_path = QtGui.QLineEdit()
        self.out_path.setPlaceholderText("path/to/save/location")
        browse_button = QtGui.QPushButton("...")
        browse_button.setObjectName('roundedButton')
        out_path_layout.addWidget(out_path_label)
        out_path_layout.addWidget(self.out_path)
        out_path_layout.addWidget(browse_button)

        # build
        build_button = QtGui.QPushButton("GENERATE PACKAGE")
        build_button.setObjectName('roundedButton')
        build_layout.addWidget(build_button)

        # signals
        self.close_button.clicked.connect(self._close_widget)
        delete_button.clicked.connect(self._delete_item)
        browse_button.clicked.connect(lambda: update_line_edit(self.out_path))
        self.password_checkbox.stateChanged.connect(self._toggle_widget)
        build_button.clicked.connect(self._build)
        save_button.clicked.connect(self._save_preset)
        self.presets.currentIndexChanged.connect(self._load_preset)

    def _load_preset(self):
        """Loads preset from combo box."""
        self.notification.clear()

        # reset package container
        package_paths = list()
        self.package_container = dict()

        preset = self.presets.currentText()
        preset_path = self._build_preset_path()
        path_to_preset_file = "{0}/{1}.json".format(preset_path, preset)
        if not os.path.isfile(path_to_preset_file):
            if preset == "-- None --":
                return self.populate_packages()
            return self.notification.setText("Preset does not exist...")

        # load data
        preset_data = json_load(path_to_preset_file)
        name = preset_data["name"]
        file_format = preset_data["format"]
        out_path = preset_data["out_path"]
        password = preset_data["password"]
        for path in preset_data["package_paths"]:
            path = convert_path(self.root_directory + path)
            package_paths.append(path)
        self.package_paths = package_paths
        root = preset_data["root"]

        # set
        self.name_line.setText(name)
        self.out_path.setText(out_path)
        if password:
            self.password.setText(password)
        format_index = self.format.findText(file_format, QtCore.Qt.MatchFixedString)
        if format_index >= 0:
            self.format.setCurrentIndex(format_index)

        # populate packages
        self.populate_packages(preset=True)

    def _save_preset(self):
        """Saves out presets."""
        self.notification.clear()

        # vars
        data = dict()
        name = self.name_line.text()
        out_path = self.out_path.text()
        file_format = self.format.currentText()
        root = os.path.basename(self.root_directory)
        password = None
        if self.password_checkbox.isChecked():
            password = self.password.text()

        # error checking
        errors = self._error_check(out_path_skip=True)
        if errors:
            return

        # build preset path
        preset_path = self._build_preset_path()
        if not os.path.isdir(preset_path):
            os.makedirs(preset_path)

        # build paths
        package_paths = list()
        for path in self.package_container.itervalues():
            partial_path = path.split(self.root_directory)[-1]
            package_paths.append(partial_path)

        # build data
        data["name"] = name
        data["format"] = file_format
        data["out_path"] = out_path
        data["password"] = password
        data["package_paths"] = package_paths
        data["root"] = root

        # save preset
        save_file = "{0}/{1}.json".format(preset_path, name)
        if os.path.isfile(save_file):
            text = "Preset exists, Overwrite?"
            warning = QtGui.QMessageBox.warning(self, "Warning", text,
                                                QtGui.QMessageBox.Yes,
                                                QtGui.QMessageBox.No)
            if warning == QtGui.QMessageBox.No:
                return self.notification.setText("Operation Canceled...")

        json_save(data, save_file)

        # repopulate presets
        self._populate_presets()
        index = self.presets.findText(name, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.presets.setCurrentIndex(index)
        self.notification.setText("Preset Saved!")

    def _build_preset_path(self):
        """Generages preset path"""
        root = os.path.basename(self.root_directory)
        if not root:
            self.root_directory = self.root_directory[:-1]
            root = os.path.basename(self.root_directory)
        return build_path("presets", root)

    def _populate_presets(self):
        """Populates the presets area"""
        preset_path = self._build_preset_path()
        if os.path.isdir(preset_path):
            for preset in os.listdir(preset_path):
                if preset.endswith(".json"):
                    preset_item = os.path.splitext(preset)[0]
                    index = self.presets.findText(preset_item,
                                        QtCore.Qt.MatchFixedString)
                    if index >= 0:
                        self.presets.removeItem(index)
                    self.presets.addItem(preset_item)

    def _error_check(self, out_path_skip=None):
        """Checks for errors"""
        # clear notifications
        self.notification.clear()

        # error checking
        name = self.name_line.text()
        out_path = self.out_path.text()
        if not name:
            self.notification.setText("please give a name...")
            return True
        if not out_path_skip:
            if not out_path:
                self.notification.setText("please give an out path...")
                return True
            if not os.path.isdir(out_path):
                self.notification.setText("please give a path on disk...")
                return True
        return False

    def _build(self):
        """Generates files"""

        # vars
        name = self.name_line.text()
        out_path = self.out_path.text()
        file_format = self.format.currentText()
        password = None
        if self.password_checkbox.isChecked():
            password = self.password.text()

        # error checking
        errors = self._error_check()
        if errors:
            return

        # build directory
        self.notification.setText("Generating Files...")
        if file_format == "-- None --":
            for path in self.package_container.itervalues():
                root = os.path.basename(self.root_directory)
                new_path = path.split(self.root_directory)[1]
                args = [out_path, name, root, new_path]
                new_path = convert_path("{0}/{1}/{2}{3}".format(*args))
                new_path_dir = os.path.dirname(new_path)
                if os.path.isfile(path):
                    if not os.path.exists(new_path_dir):
                        os.makedirs(new_path_dir)
                    shutil.copyfile(path, new_path)
                if os.path.isdir(path):
                    if not os.path.exists(new_path):
                        os.makedirs(new_path)
        # or build zip file
        elif file_format == "zip":
            archive_path = convert_path("{0}/{1}.zip".format(out_path, name))
            archive = ZipFile(archive_path, 'w', ZIP_DEFLATED, True)
            if password:
                archive.setpassword(password)
            for path in self.package_container.itervalues():
                root = os.path.basename(self.root_directory)
                new_path = path.split(self.root_directory)[1]
                new_path = convert_path("{0}/{1}".format(root, new_path))
                archive.write(path, new_path)
            archive.close()
        self.notification.setText("Process Complete!")

    def _delete_item(self):
        """deletes selected item in tree"""
        root = self.packages.invisibleRootItem()
        selected = self.packages.selectedItems()
        if not selected:
            return self.notification.setText("Please make a selection...")
        # select hierarchy
        for selected_index in xrange(len(selected)):
            base_node = selected[selected_index]
            self._select_item(base_node)

        # remove from package container
        selected = self.packages.selectedItems()
        for selected_index in xrange(len(selected)):
            base_node = selected[selected_index]
            if base_node in self.package_container:
                del self.package_container[base_node]

        # remove from list
        for item in selected:
            (item.parent() or root).removeChild(item)

    def _select_item(self, item):
        item.setSelected(True)
        for i in xrange(item.childCount()):
            child = item.child(i)
            self._select_item(child)

    def _close_widget(self):
        self.close()

    def _toggle_widget(self):
        if self.password_checkbox.isChecked():
            self.password.setEnabled(True)
        else:
            self.password.setEnabled(False)

    def populate_packages(self, widget_item=None, dir_path=None, preset=None):
        """Builds QTreeWidgetTree based off package location"""
        self.packages.clear()
        self._populate_packages(widget_item, dir_path, preset)

    def _populate_packages(self, widget_item=None, dir_path=None, preset=None):
        """Builds QTreeWidgetTree based off package location"""
        packages = dict()
        if not dir_path:
            dir_path = self.root_directory
        # handle directories
        for dir_item in os.listdir(dir_path):
            dir_item_path = convert_path("{0}/{1}".format(dir_path, dir_item))
            if os.path.isdir(dir_item_path):
                if preset:
                    if not dir_item_path in self.package_paths:
                        continue
                if not widget_item:
                    package_item = QtGui.QTreeWidgetItem(self.packages,
                                                         [dir_item])
                    icon_path = build_path('icons', 'package.png')
                    package_item.setIcon(0, QtGui.QIcon(icon_path))
                else:
                    package_item = QtGui.QTreeWidgetItem(widget_item,
                                                         [dir_item])
                    icon_path = build_path('icons', 'module.png')
                    package_item.setIcon(0, QtGui.QIcon(icon_path))
                packages[package_item] = dir_item_path
        # handle files
        for dir_item in os.listdir(dir_path):
            dir_item_path = convert_path("{0}/{1}".format(dir_path, dir_item))
            if os.path.isfile(dir_item_path):
                if preset:
                    if not dir_item_path in self.package_paths:
                        continue
                if dir_item.endswith(".pyc"):
                    continue
                if not widget_item:
                    package_file = QtGui.QTreeWidgetItem(self.packages,
                                                         [dir_item])
                else:
                    package_file = QtGui.QTreeWidgetItem(widget_item,
                                                         [dir_item])
                if dir_item.endswith(".py"):
                    icon_path = build_path('icons', 'python.png')
                    package_file.setIcon(0, QtGui.QIcon(icon_path))
                else:
                    icon_path = build_path('icons', 'file.png')
                    package_file.setIcon(0, QtGui.QIcon(icon_path))
                packages[package_file] = dir_item_path
        # recursively build
        for package_item, dir_item_path in packages.iteritems():
            if os.path.isdir(dir_item_path):
                if preset:
                    self._populate_packages(package_item, dir_item_path, True)
                else:
                    self._populate_packages(package_item, dir_item_path)
        self.package_container.update(packages)


def main():
    app = QtGui.QApplication(sys.argv)
    builder = PackageBuilder()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
