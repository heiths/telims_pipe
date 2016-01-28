#!/usr/bin/env python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    Base class for the autorig UI.
"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built in
import os
import imp
import shiboken
import pymel.core as pm
import maya.OpenMayaUI as mui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

# third party
from PySide import QtGui, QtCore

# external
import settings
from core import build_session
from modules import build_modules

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- GLOBALS --#

MODULES = list()

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class AutorigUI(object):
    """
    Base class for the Autorig UI.
    """
    def __init__(self):
        """
        The initializer.
        """
        self.image_path = settings.IMAGES
        self.module_blocks = dict()
        self.build_session = build_session.BuildSession()

    def _get_maya_window(self):
        """
        Grabs the Maya window.
        """
        pointer = mui.MQtUtil.mainWindow()
        return shiboken.wrapInstance(long(pointer), QtGui.QWidget)

    def build_gui(self, floating=False):
        """
        Builds the autorig gui.
        """
        window_name = 'telims_autorig'
        if pm.window(window_name, exists=True):
            pm.deleteUI(window_name, window=True)

        # create the window
        parent = self._get_maya_window()
        window = type(window_name,
                     (MayaQWidgetDockableMixin,
                      QtGui.QMainWindow), dict() )(parent)

        # window settings
        window.setStyleSheet('background-color: #1b1b1b;')
        window.setWindowTitle('TELIMS Autorig')
        window.setObjectName(window_name)
        window.setMinimumSize(320, 700)
        window.setMaximumWidth(320)

        # font
        font = QtGui.QFont()
        font.setPointSize(12)

        # creat main widget
        main_widget = QtGui.QWidget()
        window.setCentralWidget(main_widget)

        # main layout
        main_layout = QtGui.QVBoxLayout(main_widget)

        # module layout
        add_modules_layout = QtGui.QVBoxLayout()
        add_modules_layout.layout().setAlignment(QtCore.Qt.AlignTop)
        main_layout.layout().addLayout(add_modules_layout)

        # module menu
        modules_menu_layout = QtGui.QHBoxLayout()
        add_modules_layout.layout().addLayout(modules_menu_layout)
        modules_menu_name = QtGui.QLabel('MODULES: ')
        modules_menu = QtGui.QComboBox()
        for module in self.build_session.available_modules:
            modules_menu.addItem(module)
        modules_menu.setFixedWidth(200)
        modules_menu.setStyleSheet('background-color: #2f2f2f;')
        modules_menu_layout.addWidget(modules_menu_name)
        modules_menu_layout.addWidget(modules_menu)

        # add module button
        default_style = """
                        QPushButton{background-color: #2F2F2F;
                        border-radius: 2px; height: 30px; font-size: 16px;}
                        """
        pressed_style = """
                        QPushButton:pressed{background-color: #6f6f6f;
                        border-radius: 2px; height: 30px; font-size: 16px;}
                        """
        add_button = QtGui.QPushButton('Add Module')
        add_button.setStyleSheet(default_style + pressed_style)
        add_modules_layout.addWidget(add_button)

        # scroll layout for module UIs
        self.modules_scroll_layout = QtGui.QVBoxLayout()
        main_layout.layout().addLayout(self.modules_scroll_layout)
        self.scroll_widget = QtGui.QWidget()
        self.modules_scroll_area = QtGui.QScrollArea()
        scroll_policy = QtCore.Qt.ScrollBarAlwaysOff
        self.modules_scroll_area.setHorizontalScrollBarPolicy(scroll_policy)
        self.scroll_inside_layout = QtGui.QVBoxLayout(self.scroll_widget)
        self.scroll_inside_layout.setAlignment(QtCore.Qt.AlignTop)
        self.modules_scroll_area.setWidget(self.scroll_widget)
        self.modules_scroll_area.setWidgetResizable(True)
        self.modules_scroll_layout.addWidget(self.modules_scroll_area)
        # background
        scroll_area_background = self.image_path + 'scrollAreaBackground.png'
        scroll_area_style = ("QScrollArea{background-image: "
                             "url(" + scroll_area_background + ");}")
        self.modules_scroll_area.setStyleSheet(scroll_area_style)

        # build buttons
        build_button_layout = QtGui.QVBoxLayout()
        main_layout.layout().addLayout(build_button_layout)
        build_guides_button = QtGui.QPushButton('BUILD GUIDES')
        build_rig_button = QtGui.QPushButton('BUILD RIG')
        build_guides_button.setStyleSheet(default_style + pressed_style)
        build_rig_button.setStyleSheet(default_style + pressed_style)
        main_layout.addWidget(build_guides_button)
        main_layout.addWidget(build_rig_button)

        # connect all the buttons

        # show window
        window.show(dockable=True, floating=floating, area='left')

    def _add_module(self, *args):
        """
        """
        pass

    def _build_guides(self, *args):
        """
        """
        pass

    def _build_rig(self, *args):
        """
        """
        pass
