#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    Base class for UI constructors.
"""

#------------------------------------------------------------------------------#
#--------------------------------------------------------- APPLICATION CHECK --#

# Maya check
try:
    from maya import cmds, OpenMaya
    import maya.OpenMayaUI as mui
    MAYA = True
except ImportError:
    MAYA = False

# add more apps here

# TODO: add standalone helper function
STANDALONE = False
if not MAYA:
    STANDALONE = True

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
import os

# external
# from epic.utils import path_lib

# 3rd party
try:
    import shiboken as shiboken
except:
    import shiboken2 as shiboken
from Qt import QtGui, QtCore, QtWidgets

#------------------------------------------------------------------------------#
#----------------------------------------------------------------- FUNCTIONS --#

def _get_maya_main_window():
    """Grabs the Maya window."""
    pointer = mui.MQtUtil.mainWindow()
    return shiboken.wrapInstance(long(pointer), QtWidgets.QWidget)

def _delete_maya_widget(window_name, window_title):
    """Maya's way of handling Singletons"""
    # window
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name, window=True)
        try:
            cmds.deleteUI(window_name, control=True)
        except:
            pass

    # dock
    if cmds.dockControl(window_title, q=True, exists=True):
        cmds.deleteUI(window_title, control=True)
        try:
            cmds.deleteUI(window_name, window=True)
        except:
            pass

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class MainWindow(QtWidgets.QMainWindow):
    def keyPressEvent(self, event):
        """Override keyPressEvent to keep focus on QWidget in Maya."""
        if (event.modifiers() & QtCore.Qt.ShiftModifier):
            self.shift = True
            pass # make silent


class UIUtils(QtWidgets.QWidget):
    """Base class for UI constructors."""

    # globals
    SINGLETON = False
    MAYA_DOCK = False

    save_button = QtWidgets.QMessageBox.Yes
    multiple_selection = QtWidgets.QAbstractItemView.ExtendedSelection

    def window(self, wname=None, wtitle=None, cwidget=None, on_top=None,
               styling=None, parent=None):
        """Defines basic window parameters."""
        # maya specific
        if MAYA:
            if self.SINGLETON:
                _delete_maya_widget(wname, wtitle)
            parent = _get_maya_main_window()

        # define window
        window = MainWindow(parent)

        self.window_name = wname
        window.closeEvent = self.closeEvent

        if wname:
            window.setObjectName(wname)
        if wtitle:
            window.setWindowTitle(wtitle)
        if cwidget:
            window.setCentralWidget(cwidget)
        if on_top:
            self.set_on_top(window, on=True)
        # if styling == "dark":
            # style_sheet_file = QtCore.QFile(path_lib.aaron_dark_stylesheet)
            # style_sheet_file.open(QtCore.QFile.ReadOnly)
            # window.setStyleSheet(str(style_sheet_file.readAll()))

        if MAYA:
            window.setProperty("saveWindowPref", True)

        return window

    def maya_show(self, window, wname, wtitle, area=None):
        if not self.MAYA_DOCK:
            window.show()
        elif self.MAYA_DOCK:
            allowed_areas = ["right", "left"]
            if not area:
                area = "left"
            cmds.dockControl(wname, label=wtitle, area=area,
                             content=wname, allowedArea=allowed_areas)

    def closeEvent(self, event):
        pass

    def set_on_top(self, window, off=None, on=None):
        if off:
            args = [window.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint]
            window.setWindowFlags(*args)
            window.show()
            return
        if on:
            args = [window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint]
            window.setWindowFlags(*args)
            window.show()
            return

        # toggle
        args = [window.windowFlags() ^ QtCore.Qt.WindowStaysOnTopHint]
        window.setWindowFlags(*args)
        window.show()

    def widget(self):
        """Main Widget"""
        return QtWidgets.QWidget()

    def qt_divider_label(self, layout, label):
        """Creates a centered label header."""
        # attach to layout
        divider_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(divider_layout)

        # define divider
        divider_label = QtWidgets.QLabel(label)
        divider_label.setAlignment(QtCore.Qt.AlignCenter)
        divider_label.setMinimumHeight(20)
        divider_left = QtWidgets.QFrame()
        divider_left.setFrameShape(QtWidgets.QFrame.HLine)
        divider_left.setFrameShadow(QtWidgets.QFrame.Sunken)
        divider_right = QtWidgets.QFrame()
        divider_right.setFrameShape(QtWidgets.QFrame.HLine)
        divider_right.setFrameShadow(QtWidgets.QFrame.Sunken)
        divider_layout.addWidget(divider_left)
        divider_layout.addWidget(divider_label)
        divider_layout.addWidget(divider_right)

    def qt_list_widget_add_items(self, widget, items, clear=None, dup=None):
        """Qt Wrapper for QListWidget for adding items."""
        if clear:
            self.clear_widget(widget)
        for item_text in items:
            item = QtWidgets.QListWidgetItem(item_text)
            if dup:
                if widget.findItems(item.text(), QtCore.Qt.MatchExactly):
                    continue
            widget.addItem(item)

    def list_widget_find_all_items(self, widget, index=None):
        """Finds all items in a QListWidget"""
        all_items = list()
        all_items_dict = dict()
        for count in xrange(widget.count()):
            if index:
                item_name = widget.item(count).text()
                all_items_dict[item_name] = count
                continue
            all_items.append(widget.item(count).text())
        if index:
            return all_items_dict
        return all_items

    def combo_widget_find_all_items(self, widget, index=None):
        """Finds all items in a QListWidget"""
        all_items = list()
        all_items_dict = dict()
        for count in xrange(widget.count()):
            if index:
                item_name = widget.itemText(count)
                all_items_dict[item_name] = count
                continue
            all_items.append(widget.itemText(count))
        if index:
            return all_items_dict
        return all_items

    def qt_list_widget_remove_items(self, widget):
        """Qt Wrapper for QListWidget for removing items"""
        for item in widget.selectedItems():
            widget.takeItem(widget.row(item))

    def clear_widget(self, widget):
        """Clears items in a widget."""
        widget.clear()

    def warning(self, message, button_one=None, button_two=None):
        """Method for prompting the user with a warning."""
        if not button_one:
            button_one = QtWidgets.QMessageBox.Ok
        if not button_two:
            button_two = QtWidgets.QMessageBox.Cancel
        args = [self, "Warning", message, button_one, button_two]
        warning = QtWidgets.QMessageBox.warning(*args)
        return warning

    def widget_state(self, widgets, state=None, exclude=None):
        """Enables/Disables Widgets based on their current state.
            @PARAMS:
                :widgets: list, widgets.
                :state: "disable", "enable", None = toggle
        """
        for widget in widgets:
            if exclude:
                if widget in exclude:
                    continue
            if state == "disable":
                widget.setEnabled(False)
            elif state == "enable":
                widget.setEnabled(True)
            else: # toggle
                if widget.isEnabled():
                    widget.setEnabled(False)
                elif not widget.isEnabled():
                    widget.setEnabled(True)

    def header_image(self, layout, path):
        """Creates header image."""
        label = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(path)
        label.setPixmap(pixmap)

        layout.addWidget(label)

    def browse(self, line_widget):
        """Finds export path and populates QLineEdit"""
        save_directory = QtWidgets.QFileDialog.getExistingDirectory()
        if save_directory:
            line_widget.setText(save_directory)
        return save_directory

    @classmethod
    def clear_settings(cls, settings, info=None):
        """Clears out the Epic Games Menu settings"""
        settings.clear()
        if not info:
            info = "Settings have been Reset."
        if MAYA:
            OpenMaya.MGlobal.displayWarning(info)

    @classmethod
    def get_open_filename(cls, cap, file_filter, start_path=None,
                          existing_dir=None):
        """File Dialog that returns selected path."""

        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setLabelText(QtWidgets.QFileDialog.Accept, "Import")
        if existing_dir:
            args = [file_dialog, cap]
            return file_dialog.getExistingDirectory(*args)
        if not start_path:
            start_path = QtCore.QDir.currentPath()
        args = [file_dialog, cap, start_path, file_filter]
        return file_dialog.getOpenFileName(*args)


