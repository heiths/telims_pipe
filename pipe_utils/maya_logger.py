#!/usr/bin/python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle
:description:
    IO operations for piping information to either a log file or a console.

    @PARAMS:
        :message: str, list, the information you want to keep.
        :exc_info: bool, traceback.
        :title: str, title of the output.
        :pretty: bool, if it's a list, it'll pretty print it to the log.
"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# build-in
import tempfile
import sys, os
import logging
import random

# third-party
from maya import cmds
from PySide import QtCore, QtGui

# external
import abc_pipe
from pipe_utils.ui_utils import UIUtils

#------------------------------------------------------------------------------#
#----------------------------------------------------------------- QTHANDLER --#

class QtHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        record = self.format(record)
        if record: XStream.stdout().write("{0}\n".format(record))
        # if issues use: XStream.stdout().write('%s\n'%record)

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- GLOBALS --#

# output
DIVIDER = "<br> -------------------------------------------------------------- "

# set logger
LOGGER = logging.getLogger(__name__)
HANDLER = QtHandler()
HANDLER.setFormatter(logging.Formatter("%(message)s"))
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.DEBUG)

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class XStream(QtCore.QObject):
    """XStream Wrapper"""
    _stdout = None
    _stderr = None
    messageWritten = QtCore.Signal(str)

    def flush(self):
        pass

    def fileno(self):
        return -1

    def write(self, message):
        if not self.signalsBlocked():
            self.messageWritten.emit(message)

    @staticmethod
    def stdout():
        if not XStream._stdout:
            XStream._stdout = XStream()
            sys.stdout = XStream._stdout
        return XStream._stdout

    @staticmethod
    def stderr():
        if not XStream._stderr:
            XStream._stderr = XStream()
            sys.stderr = XStream._stderr
        return XStream._stderr

class MayaLogger(UIUtils):
    def __init__(self, parent=None, file_logging=False, path=None):
        """Logging Entry Point
            @PARAMS:
                file_logging: bool, if True, will log.
                path: str, path to log file.
        """

        # reset logging system
        logging.shutdown()
        reload(logging)

        # super
        super(MayaLogger, self).__init__(parent=parent)

        # file logging
        self.file_logging = file_logging
        self.file_logger = None
        self.console = None
        self.path = path
        if not self.path:
            checksum = random.randrange(100000, 999999)
            file_name = "MayaLogging_{0}.log".format(random.randrange(checksum))
            self.path = "{0}/{1}".format(tempfile.gettempdir(), file_name)
        self.file_logger = logging.getLogger("MayaLoggingFile")
        self.file_handler = logging.FileHandler(self.path)

        # create logger instance and file location
        if self.file_logging:
            self._enable_file_logging()
        else:
            self._disable_logging()
            os.remove(self.path)

    def terminal(self):

        # window args
        window_name = "maya_logger"
        window_title = "Maya Logger"
        widget = self.widget()

        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name, window=True)

        # use dialog for modal
        window = self.window(window_name, window_title, widget)
        window.setMinimumSize(500, 700)

        # layout
        layout = QtGui.QVBoxLayout(widget)

        self.qt_divider_label(layout, "Welcome to the ABC Logger")

        # console
        self.console = QtGui.QTextBrowser()
        self.console.setStyleSheet("background-color: black")
        layout.addWidget(self.console)
        window.setLayout(layout)

        # buttons
        button_layout = QtGui.QHBoxLayout()
        layout.addLayout(button_layout)

        clear_log_button = QtGui.QPushButton("Clear Log")
        self.open_log_file = QtGui.QPushButton("Open Log File")
        self.open_log_file.setEnabled(False)

        self.enable_file_logging = QtGui.QCheckBox("Enable File Logging")
        self.file_logging = False
        self.enable_file_logging.setMaximumWidth(130)

        button_layout.addWidget(clear_log_button)
        button_layout.addWidget(self.open_log_file)
        button_layout.addWidget(self.enable_file_logging)

        # signals
        clear_log_button.clicked.connect(self._clear)
        self.open_log_file.clicked.connect(self._open_log_file)

        # enable file logging
        self.enable_file_logging.stateChanged.connect(self._enable_file_logging)


        # xtream wrapper signal
        XStream.stdout().messageWritten.connect(self.console.insertHtml)
        XStream.stderr().messageWritten.connect(self.console.insertHtml)

        # show debugger
        window.show()

    def debug(self, message, exc_info=False, title="DEBUG", pretty=False):
        """DEBUG, for full verbosity level."""

        debug_text = self._message(message, title, "orange", exc_info)
        LOGGER.debug(debug_text, exc_info=exc_info)

    def info(self, message, exc_info=False, title="INFO", pretty=False):
        """INFO, for simply outputting information."""
        debug_text = self._message(message, title, "green", exc_info, pretty)
        LOGGER.info(debug_text, exc_info=exc_info)

    def warning(self, message, exc_info=False, title="WARNING", pretty=False):
        """WARNING, level 1 verbosity."""
        debug_text = self._message(message, title, "yellow", exc_info)
        LOGGER.warning(debug_text, exc_info=exc_info)

    def error(self, message, exc_info=False, title="ERROR", pretty=False):
        """ERROR, level 2 verbosity."""
        debug_text = self._message(message, title, "red", exc_info)
        LOGGER.error(debug_text, exc_info=exc_info)

    def _message(self, message, level, color, exc_info, pretty=False):
        """Builds outlog for the terminal and file logging."""
        if isinstance(message, list):
            if pretty:
                for count, item in enumerate(message):
                    message[count] = item + "<br>"
                message = ''.join(str(e) for e in message)

        if self.file_logging:
            self.file_logger.debug(message, exc_info=exc_info)
        logging_html = '''<br><span style="color: {0}; align: left;">'''.format(color)
        logging_html += "<br>{0} {1} <br>".format(level, DIVIDER)
        logging_html += "{0} <br></span>".format(str(message))
        return logging_html

    def _clear(self):
        self.clear_widget(self.console)

    def _enable_file_logging(self):
        """Enables file logging."""

        # create logging instance and add it to the handler
        self.file_logger.addHandler(self.file_handler)
        file_formatter = logging.Formatter("%(asctime)s %(levelname)s \n %(message)s")
        self.file_handler.setFormatter(file_formatter)
        self.file_logger.setLevel(logging.DEBUG)

        try:
            self.widget_state([self.open_log_file])
            if self.enable_file_logging.isChecked():
                self.file_logging = True
                self.info(self.path, title="LOG ENABLED")
            else:
                self.warning(self.path, title="LOG FILE DELETED")
                logging.shutdown()
                os.remove(self.path)
        except AttributeError, e:
            self.warning(e, True)

    def _disable_logging(self):
        """Disables logging"""
        logging.shutdown()

    def _open_log_file(self):
        os.startfile(self.path)

def main():

    # build logging system
    logger = MayaLogger()
    terminal = logger.terminal()

    return logger

if __name__ == '__main__':
    main()
