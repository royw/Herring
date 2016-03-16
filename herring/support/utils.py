# coding=utf-8

"""
Various utility functions
"""

import fnmatch
import os
import re

__docformat__ = 'restructuredtext en'


def find_files(directory, includes=None, excludes=None):
    """
    Find files given a starting directory and optionally a set of includes and/or excludes patterns.

    The patterns should be globs (ex: ['*.py', '*.rst'])

    :param directory: the starting directory for the find
    :type directory: str
    :param includes: list of file glob patterns to find
    :type includes: list
    :param excludes: list of file or directory glob patterns to exclude
    :type excludes: list
    :return: iterator of found file paths as strings
    :rtype: iterator(str)
    """
    if includes is None:
        includes = []
    if excludes is None:
        excludes = []
        # transform glob patterns to regular expressions
    includes = r'|'.join([fnmatch.translate(x) for x in includes])
    excludes = r'|'.join([fnmatch.translate(x) for x in excludes]) or r'$.'

    for root, dirs, files in os.walk(directory):
        # exclude dirs
        dirs[:] = [os.path.join(root, d) for d in dirs]
        dirs[:] = [d for d in dirs if not re.match(excludes, d)]

        # exclude/include files
        files = [os.path.join(root, f) for f in files]
        files = [f for f in files if not re.match(excludes, f)]
        files = [f for f in files if re.match(includes, f)]

        for filename in files:
            yield filename
