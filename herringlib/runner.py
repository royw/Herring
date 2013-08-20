import os
from herring.support.SimpleLogger import info


def system(cmd_line, verbose=True):
    """simple system runner with verbose"""
    if verbose:
        info(cmd_line)
    result = os.popen(cmd_line).read()
    if verbose:
        info(result)
    return result
