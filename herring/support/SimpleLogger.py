# coding=utf-8
"""
Simple logger to the stderr stream.
"""
import sys

LogOutputter = {
    'debug': [],
    'info': [sys.stdout],
    'warning': [sys.stdout],
    'error': [sys.stderr],
    'fatal': [sys.stderr],
}

currentComponent = None
showLevel = False


def setVerbose(verbose=True):
    """
    set verbose mode
    :param verbose: if verbose, then info messages are sent to stdout.
     :type verbose: bool
    """
    if verbose:
        LogOutputter['info'] = [sys.stdout]
    else:
        LogOutputter['info'] = []


def setDebug(debug=True):
    """
    set debug logging mode

    :param debug: if debug, then debug messages are sent to stdout.
    """
    if debug:
        LogOutputter['debug'] = [sys.stdout]
        LogOutputter['info'] = [sys.stdout]
    else:
        LogOutputter['debug'] = []


def setComponent(component=None):
    """
    set component label

    :param component: the component label to insert into the message string.
    """
    global currentComponent
    currentComponent = component


def setShowLevel(on=True):
    """
    enable showing the logging level

    :param on: if on, then include the log level of the message (DEBUG, INFO, ...) in the output.
    """
    global showLevel
    showLevel = on


def _output(level, message):
    buf = []
    if showLevel:
        buf.append("{level}:  ".format(level=level.upper()))
    if currentComponent:
        buf.append("[{component}]  ".format(component=str(currentComponent)))
    buf.append(str(message))
    buf.append("\n")
    line = ''.join(buf)
    for outputter in LogOutputter[level]:
        outputter.write(line)


def debug(message):
    """
    debug message

    :param message: the message to emit
     :type message: object that can be converted to a string using str()
    """
    _output('debug', message)


def info(message):
    """
    info message

    :param message: the message to emit
     :type message: object that can be converted to a string using str()
    """
    _output('info', message)


def warning(message):
    """
    warning message

    :param message: the message to emit
     :type message: object that can be converted to a string using str()
    """
    _output('warning', message)


def error(message):
    """
    error message

    :param message: the message to emit
     :type message: object that can be converted to a string using str()
    """
    _output('error', message)


def fatal(message):
    """
    fatal message

    :param message: the message to emit
     :type message: object that can be converted to a string using str()
    """
    _output('fatal', message)
    exit(1)
