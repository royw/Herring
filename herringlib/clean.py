# coding=utf-8

"""
Clean tasks
-----------

clean() removes \*.pyc and \*\~ files.

purge() additionally removes the generated api and quality directories.
"""
import os
import shutil
from herring.herring_app import task, HerringFile
from herring.support.SimpleLogger import debug
from herringlib.recursively_remove import recursively_remove


global Project


@task()
def clean():
    """ remove build artifacts """
    recursively_remove(HerringFile.directory, '*.pyc')
    recursively_remove(HerringFile.directory, '*~')
    debug(repr(Project.__dict__))

    dirs = [Project.distDir, Project.buildDir, Project.eggDir]
    # print "dirs => %s" % repr(dirs)

    for dir_name in dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)


@task(depends=['clean'])
def purge():
    """ remove unnecessary files """
    if os.path.exists(Project.apiDir):
        shutil.rmtree(Project.apiDir)

    if os.path.exists(Project.qualityDir):
        shutil.rmtree(Project.qualityDir)


