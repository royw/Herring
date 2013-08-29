# coding=utf-8

"""
Find files helper function.

Usage
-----

You must specify the directory to start recursively searching in.
You may specify a list of excluded directories and/or files.  These may be glob patterns.
You may specify a list of included files.  These may be glob patterns.

Exclusion is performed before inclusion.

Examples
--------

Find all files in the given directory, dir, and it's sub-directories::

    findFiles(dir)

Find all files in the given directory, dir, but excluding any subversion files::

    findFiles(dir, excludes=['.svn'])

Find all files ending in '.py'::

    findFiles(dir, includes=['*.py'])

Find all '.py' files but excluding any subversion files::

    findFiles(dir, excludes=['.svn'], includes=['*.py'])

Find all source files::

    findFiles(dir, excludes=['.git', '.svn'], includes=['*.py', '*.rst'])

"""

__docformat__ = 'restructuredtext en'

import fnmatch
import os
import re


def findFiles(directory, includes=None, excludes=None):
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
