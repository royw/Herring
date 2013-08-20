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
    if verbose:
        LogOutputter['info'] = [sys.stdout]
    else:
        LogOutputter['info'] = []


def setDebug(debug=True):
    if debug:
        LogOutputter['debug'] = [sys.stdout]
    else:
        LogOutputter['debug'] = []


def setComponent(component=None):
    global currentComponent
    currentComponent = component


def setShowLevel(on=True):
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
    _output('debug', message)


def info(message):
    _output('info', message)


def warning(message):
    _output('warning', message)


def error(message):
    _output('error', message)


def fatal(message):
    _output('fatal', message)
    exit(1)
