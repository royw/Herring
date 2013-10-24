# coding=utf-8

"""
Provides built in run support methods for herringfile tasks.
"""
import fcntl
from herring.support.graceful_interrupt_handler import GracefulInterruptHandler

__docformat__ = 'restructuredtext en'

import os
import subprocess
import sys
from herring.support.simple_logger import info

__all__ = ('HerringFile',)


#noinspection PyPep8Naming
class HerringFile(object):
    """Run helper"""
    directory = ''

    uninstalled_packages = []
    installed_packages = None

    @classmethod
    def _nonBlockRead(cls, output):
        fd = output.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        #noinspection PyBroadException
        try:
            return output.read()
        except:
            return ''

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
        if verbose:
            info("cmd_args => %s" % repr(cmd_args))
            info("env => %s" % repr(env))
            info("verbose => %s" % repr(verbose))
            info(' '.join(cmd_args))
        lines = []
        for line in cls.runProcess(cmd_args, env=env, verbose=verbose):
            if verbose:
                sys.stdout.write(line)
                sys.stdout.flush()
            lines.append(line)

        return "".join(lines)

    @classmethod
    def runProcess(cls, exe, env=None, verbose=True):
        """
        Run the process yield for each output line from the process.

        :param cls: class name
        :type cls: class
        :param exe: command line components
        :type exe: list
        :param env: environment
        :type env: dict
        :param verbose: outputs the method call if True
        :type verbose: bool
        """
        if verbose:
            info("runProcess(%s, %s)" % (exe, env))
        sub_env = os.environ.copy()
        if env:
            for key, value in env.iteritems():
                sub_env[key] = value

        with GracefulInterruptHandler() as handler:
            process = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       env=sub_env)
            while process.poll() is None:   # returns None while subprocess is running
                if handler.interrupted:
                    process.kill()
                while True:
                    line = HerringFile._nonBlockRead(process.stdout)
                    if not line:
                        break
                    yield line

    @classmethod
    def packagesRequired(cls, package_names):
        """
        Check that the give packages are installed.

        :param package_names: the package names
        :type package_names: list
        :return: asserted if all the packages are installed
        :rtype: bool
        """
        result = True

        packages = cls.run(['yolk', '-l'], verbose=False).split("\n")
        if cls.installed_packages is None:
            cls.installed_packages = [name.split()[0].lower() for name in packages if name]

        # info("installed_packages: %s" % repr(cls.installed_packages))

        for pkg_name in package_names:
            if pkg_name.lower() not in cls.installed_packages:
                print(pkg_name + " not installed!")
                result = False
        return result
