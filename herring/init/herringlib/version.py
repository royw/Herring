# coding=utf-8
"""
Package version support.

Provides *version* and *bump* tasks.

Old style used a package/VERSION.txt file that contained a version string.
This old style is deprecated to the more pythoneese style of having a global __version__
attribute located in package/__init__.py.

Usage:

.. code-block: python

    package_name = 'root_package'
    setProjectVersion('0.1.2', package_name)
    ver = getProjectVersion(package_name)
    print('# Version: %s' % ver)
    # Version: 0.1.2
    bump()
    print('# Version: %s' % getProjectVersion(package_name)
    # Version: 0.1.3

.. code-block: bash

    ➤ grep version root_package/__init__.py
    __version__ = '0.1.3'

"""

__docformat__ = 'restructuredtext en'

import os
import re
from herring.herring_app import task, HerringFile
from herring.init.herringlib.safe_edit import safeEdit
from herring.support.simple_logger import info, error, debug


# pylint: disable=W0604,E0602
global Project

VERSION_REGEX = r'__version__\s*=\s*[\'\"](\S+)[\'\"]'


def _fileSpec(basename, project_package=None):
    """build the file spec in the project"""
    parts = [HerringFile.directory, project_package, basename]
    return os.path.join(*[f for f in parts if f is not None])


def getProjectVersion(project_package=None):
    r"""
    Get the version from __init__.py with a line: /^__version__\s*=\s*(\S+)/
    If it doesn't exist try to load it from the VERSION.txt file.
    If still no joy, then return '0.0.0'

    :param project_package: the root package
    :type project_package: str
    :returns: the version string
    :rtype: str
    """

    # trying __init__.py first
    try:
        file_name = _fileSpec('__init__.py', project_package)
        debug("version_file => %s" % file_name)
        with open(file_name, 'r') as in_file:
            for line in in_file.readlines():
                match = re.match(VERSION_REGEX, line)
                if match:
                    return match.group(1)
    except IOError:
        pass

    # no joy, so try getting the version from a VERSION.txt file.
    try:
        file_name = _fileSpec('VERSION.txt', project_package)
        info("version_file => %s" % file_name)
        with open(file_name, 'r') as in_file:
            return in_file.read().strip()
    except IOError:
        pass

    # no joy again, so set to initial version and try again
    setProjectVersion('0.0.1', project_package)
    return getProjectVersion(project_package)


def setProjectVersion(version_str, project_package=None):
    """
    Set the version in __init__.py

    :param version_str: the new version string
    :type version_str: str
    :param project_package: the root package
    :type project_package: str
    """

    def versionLine(version_str):
        """
        return python line for setting the __version__ attribute

        :param version_str: the version string
         :type version_str: str
        """
        return "__version__ = '{version}'".format(version=version_str)

    try:
        file_name = _fileSpec('__init__.py', project_package)
        with safeEdit(file_name) as files:
            replaced = False
            for line in files['in'].readlines():
                match = re.match(VERSION_REGEX, line)
                if match:
                    line = re.sub(VERSION_REGEX, versionLine(version_str), line)
                    replaced = True
                files['out'].write(line)
            if not replaced:
                files['out'].write("\n")
                files['out'].write(versionLine(version_str))
                files['out'].write("\n")

        file_name = _fileSpec('VERSION.txt', project_package)
        if os.path.exists(file_name):
            os.remove(file_name)

    except IOError as ex:
        error(ex)


@task()
def bump():
    """
    Bumps the patch version in VERSION file up by one.
    If the VERSION file does not exist, then create it and initialize the version to '0.0.0'.
    """
    version_str = getProjectVersion(project_package=Project.package)
    parts = version_str.split('.')
    parts[-1] = str(int(parts[-1]) + 1)
    setProjectVersion('.'.join(parts), project_package=Project.package)
    Project.version = getProjectVersion(project_package=Project.package)
    info("Bumped version from %s to %s" % (version_str, Project.version))


@task()
def version():
    """Show the current version"""
    info("Current version is: %s" % getProjectVersion(project_package=Project.package))
