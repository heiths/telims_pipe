#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    System Utilities.
"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
import os
import sys
import json
import shutil

# third-party
# batch hack
try: from maya import cmds
except: pass

#------------------------------------------------------------------------------#
#----------------------------------------------------------------- FUNCTIONS --#

def json_save(data=None, path=None):
    """Saves out given data into a json file."""
    # batch hack
    try:
        if not path:
            path = cmds.fileDialog2(fm=0, ds=2, ff="*.json", rf=True)
            if not path:
                return
            path = path[0]
    except:
        pass
     
    data = json.dumps(data, sort_keys=True, ensure_ascii=True, indent=2)
    fobj = open(path, 'wb')
    fobj.write(data)
    fobj.close()

    return path

def json_load(path=None):
    """This procedure loads and returns the content of a json file."""
    # batch hack
    try:
        if not path:
            path = cmds.fileDialog2(fm=1, ds=2, ff="*.json")
            if not path:
                return
            path = path[0]
    except:
        pass

    fobj = open(path, "rb")
    data = json.load(fobj)
    return data

def win_path_convert(path=None):
    """Converts \ to /"""
    separator = os.sep
    if separator != "/":
        path = path.replace(os.sep, "/")
    return path

def reset_all_modules():
    """Resets all system modules, used for reloading."""
    if globals().has_key('init_modules'):
        for m in [x for x in sys.modules.keys() if x not in init_modules]:
            del(sys.modules[m])
    else:
        init_modules = sys.modules.keys()

def build_path(folder, name):
    return win_path_convert(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                     folder, name))

def stomp_copy(source, destination, stomp=True):
    """Copies file to and from.
    @PARAMS:
        source: str(path)
        destination: str(path)
        stomp: bool, delete file if it exists already."""

    if not os.path.exists(from_path) or not os.path.exists(to_path):
        return "The source path:{0} does not exists.".format(from_path)
    elif not os.path.exists(to_path):
        return "The destination path:{0} does not exists.".format(to_path)
    if stomp:
        return shutil.copyfile(source, destination)
    return source
