# coding=utf-8

"""
Provides built in run support methods for herringfile tasks.
"""
import pkgutil

__docformat__ = 'restructuredtext en'

import os
import subprocess
import sys
from herring.support import utils
from herring.support.simple_logger import info

__all__ = ('HerringFile',)


class HerringFile(object):
    """Run helper"""
    directory = ''

    uninstalled_packages = []

    @classmethod
    def run(cls, cmd_args, env=None, verbose=True):
        """
        Down and dirty shell runner.  Yeah, I know, not pretty.

        :param cmd_args: list of command arguments
        :type cmd_args: list
        :param env: the environment variables for the command to use.
        :type env: dict
        :param verbose: if verbose, then echo the command and it's output to stdout.
        :type verbose: bool
        """
        info("cmd_args => %s" % repr(cmd_args))
        info("env => %s" % repr(env))
        info("verbose => %s" % repr(verbose))
        if verbose:
            info(' '.join(cmd_args))
        lines = []
        for line in cls.runProcess(cmd_args, env=env):
            if verbose:
                sys.stdout.write(line)
            lines.append(line)
        return "".join(lines)

    @classmethod
    def runProcess(cls, exe, env=None):
        """
        Run the process yield for each output line from the process.

        :param cls: class name
        :type cls: class
        :param exe: command line components
        :type exe: list
        :param env: environment
        :type env: dict
        """
        info("runProcess(%s, %s)" % (exe, env))
        sub_env = os.environ.copy()
        if env:
            for key, value in env.iteritems():
                sub_env[key] = value

        process = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   env=sub_env)
        while True:
            ret_code = process.poll()   # returns None while subprocess is running
            line = process.stdout.readline()
            yield line
            if ret_code is not None:
                break

    @classmethod
    def findFiles(cls, directory, includes=None, excludes=None):
        """
        Find files given a starting directory and optionally a set of includes and/or excludes patterns.

        The patterns should be globs (ex: ['*.py', '*.rst'])

        :param directory: the starting directory for the find
        :type directory: str
        :param includes: list of file glob patterns to find
        :type includes: list(str)
        :param excludes: list of file or directory glob patterns to exclude
        :type excludes: list(str)
        :return: iterator of found file paths as strings
        :rtype: iterator(str)
        """
        return utils.findFiles(directory, includes, excludes)

    @classmethod
    def packagesRequired(cls, package_names):
        """
        Check that the give packages are installed.

        :param package_names: the package names
        :type package_names: list(str)
        :return: asserted if all the packages are installed
        :rtype: bool
        """
        result = True
        for package_name in [name for name in package_names if name not in pkgutil.iter_modules(name)]:
            print "Package \"{name}\" not installed!".format(name=package_name)
            cls.uninstalled_packages.append(package_name)
            result = False
        return result


