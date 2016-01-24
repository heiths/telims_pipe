#!/usr/bin/env python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    Responsible for the actual build session.
"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
import os
import glob
import pymel.core as pm

# external
import settings

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class BuildSession(object):
    """
    Base class for the build session.
    """
    def __init__(self):
        """
        The initializer.
        """
        self.modules = list()
        self.folders_to_exclude = ["build_modules"]
        self.files_to_exclude = ["__init__.py"]
        self.modules_dic = dict()
        self.available_modules = list()

        # let's begin
        self._get_avaliable_modules()
        print self.available_modules

    def _get_avaliable_modules(self):
        """
        Looks for all the available modules.
        """
        path = settings.MODULES
        if os.path.exists(path):
            self._check_path(path)

    def _check_path(self, path):
        """
        Checks the given path for any py files.
        """
        path_files = os.listdir(path)
        modules = list()
        for path_file in path_files:
            if os.path.isdir(path + path_file)
                if path_file not in self.folders_to_exclude:
                    self._check_path(path + path_file)
            if path_file.endswith(".py"):
                modules.append(path_file)
                self.modules_dic[path_file] = path + path_file

        # store the available modules
        self.available_modules += modules


