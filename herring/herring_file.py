# coding=utf-8

"""
Provides built in run support methods for herringfile tasks.
"""
import os
import subprocess
import sys
from herring.support.SimpleLogger import info

__all__ = ('HerringFile',)


class HerringFile(object):
    """Run helper"""
    directory = ''

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

        p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             env=sub_env)
        while True:
            ret_code = p.poll()   # returns None while subprocess is running
            line = p.stdout.readline()
            yield line
            if ret_code is not None:
                break


