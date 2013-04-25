import os
import re
import subprocess
import sys
from urllib import urlopen

from herring.support.appVersion import AppVersion


def package_update(package_name, package_script, package_repository):
    """ update herring to the latest available """
    url = package_repository
    handle = urlopen(url + "/")
    versions = []
    for line in handle.readlines():
        match_obj = re.match(r".*%s\-(\d+\.\d+\.\d+)\.tar.gz" %
                             package_name, line)
        if match_obj:
            versions.append(AppVersion(match_obj.group(1)))
    latest = sorted(versions)[-1]
    print "latest %s version is %s" % (package_script, latest)
    version_str = run("%s --version" % package_script, verbose=False)
    match_obj = re.match(r'.*(\d+\.\d+\.\d+)', version_str)
    if match_obj:
        current = AppVersion(match_obj.group(1))
        print "current %s version is %s" % (package_script, current)
        if latest > current:
            run("pip install --upgrade %s/%s-%s.tar.gz" %
                (url, package_name, latest))


# # just a support function, not a task
# def run(cmd_line, verbose=True):
#     """ Down and dirty shell runner.  Yeah, I know, not pretty. """
#     if verbose:
#         print cmd_line
#     lines = []
#     for line in runProcess(cmd_line.split(" ")):
#         if verbose:
#             sys.stdout.write(line)
#         lines.append(line)
#     return "".join(lines)
#
#
# def runProcess(exe):
#     p = subprocess.Popen(exe, stdout=subprocess.PIPE,
#                          stderr=subprocess.STDOUT)
#     while True:
#         ret_code = p.poll()   # returns None while subprocess is running
#         line = p.stdout.readline()
#         yield line
#         if ret_code is not None:
#             break

def system(cmd_line, verbose=True):
    """simple system runner with verbose"""
    if verbose:
        print cmd_line
    result = os.popen(cmd_line).read()
    if verbose:
        print result
    return result


# just a support function, not a task
def run(cmd_args, env=None, verbose=True):
    """ Down and dirty shell runner.  Yeah, I know, not pretty. """
    print "cmd_args => %s" % repr(cmd_args)
    print "env => %s" % repr(env)
    print "verbose => %s" % repr(verbose)
    if verbose:
        print ' '.join(cmd_args)
    lines = []
    for line in runProcess(cmd_args, env=env):
        if verbose:
            sys.stdout.write(line)
        lines.append(line)
    return "".join(lines)


def runProcess(exe, env=None):
    print("runProcess(%s, %s)" % (exe, env))
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
