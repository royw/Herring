# coding=utf-8

"""
Run external scripts and programs.
"""
import os
from herring.support.SimpleLogger import info


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
