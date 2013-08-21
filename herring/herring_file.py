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
        """ Down and dirty shell runner.  Yeah, I know, not pretty. """
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


