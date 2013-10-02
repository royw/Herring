# coding=utf-8

"""
Run external scripts and programs.
"""
from herring.herring_app import run

__docformat__ = 'restructuredtext en'

import os
from herring.support.simple_logger import info


def system(cmd_line, verbose=True):
    """
    simple system runner with optional verbose echo of command and results.

    Execute the given command line and wait for completion.

    :param cmd_line: command line to execute
    :type cmd_line: str
    :param verbose: asserted to echo command and results
    :type verbose: bool
    """
    if verbose:
        info(cmd_line)
    result = os.popen(cmd_line).read()
    if verbose:
        info(result)
    return result


def script(cmdline, env=None):
    """
    Simple runner using the *script* utility to preserve color output by letting the
    command being ran think it is running on a console instead of a tty.

    See: man script

    :param cmdline: command line to run
    :type cmdline: str
    :param env: environment variables or None
    :type env: list
    :return: the output of the command line
    :rtype: str
    """
    run(['script', '-q', '-e', '-f', '-c', cmdline], env)
