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
    """set verbose mode"""
    if verbose:
        LogOutputter['info'] = [sys.stdout]
    else:
        LogOutputter['info'] = []


def setDebug(debug=True):
    """set debug logging mode"""
    if debug:
        LogOutputter['debug'] = [sys.stdout]
    else:
        LogOutputter['debug'] = []


def setComponent(component=None):
    """set component label"""
    global currentComponent
    currentComponent = component


def setShowLevel(on=True):
    """enable showing the logging level"""
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
    """debug message"""
    _output('debug', message)


def info(message):
    """info message"""
    _output('info', message)


def warning(message):
    """warning message"""
    _output('warning', message)


def error(message):
    """error message"""
    _output('error', message)


def fatal(message):
    """fatal message"""
    _output('fatal', message)
    exit(1)
