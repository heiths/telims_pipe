#!/usr/bin/python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    useful decorators to inhance code functionality.

"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built in
import time

# third party
from maya import cmds, mel
from functools import wraps

#------------------------------------------------------------------------------#
#---------------------------------------------------------------- DECORATORS --#

def undo(function):
    def wrapper(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        try:
            return_function = function(*args, **kwargs)
        finally:
            cmds.undoInfo(closeChunk=True)
        return return_function
    return wrapper

def timeit(function):
    def wrapper(*args, **kw):
        # time it
        time_start = time.time()
        return_function = function(*args, **kw)
        time_end = time.time()

        # report
        elapsed_time = time_end - time_start
        print "{0} sec".format(elapsed_time)
        return return_function
    return wrapper

def repeat_last(function):
    """Makes functions inside UI's repeatable in Maya."""
    def wrapper(*args, **kwargs):
        function_return = None
        arg_string = ''
        if args:
            for each in args:
                arg_string += str(each)+', '
        if kwargs:
            for key, item in kwargs.iteritems():
                arg_string += str(key)+'='+str(item)+', '

        import_path = function.__module__
        command_to_repeat = 'python("from '+import_path+' import \
                            '+function.__name__+'");'
        command_to_repeat += 'python("'+function.__name__+'('+arg_string+')")'
        function_return = function(*args, **kwargs)
        try:
            cmds.repeatLast(ac=command_to_repeat, acl=function.__name__)
        except:
            pass
        return function_return
    return wrapper

def viewport_off(function):
    """
    Decorator - turn off Maya display while func is running.
    if func will fail, the error will be raised after.
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        # Turn $gMainPane Off:
        mel.eval("paneLayout -e -manage false $gMainPane")
        try:
            return function(*args, **kwargs)
        except Exception:
            raise
        finally:
            mel.eval("paneLayout -e -manage true $gMainPane")
    return wrapper
