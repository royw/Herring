# coding=utf-8

"""
Helper for verifying that 3rd party applications are available for use.
"""

__docformat__ = 'restructuredtext en'

from herring.init.herringlib.runner import system
from herring.support.simple_logger import warning

HELP = {
    'pynsource': "pyNsource generates class diagrams.  "
                 "Please install from http://www.andypatterns.com/index.php/products/pynsource/",
    'pyreverse': 'pyreverse generates package and class UML diagrams and is part of pylint.  Please install pylint.',
    'rstlint': 'rstlint checks the RST in the given file.  '
               'Please install from http://svn.python.org/projects/python/trunk/Doc/tools/'
}


def executablesAvailable(executable_list):
    """
    Check if the given applications are on the path using the 'which' command.
    :param executable_list: list of application names
    :type executable_list: list of str instances
    :return: asserted if all are available
    :rtype: bool
    """
    for executable in executable_list:
        if not system("which {name}".format(name=executable), verbose=False).strip():
            warning(HELP[executable])
            return False
    return True
