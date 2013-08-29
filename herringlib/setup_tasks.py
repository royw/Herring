# coding=utf-8
"""
Set of Herring tasks for packaging a project.

In early development, the install/uninstall tasks are useful.
Less so after you start deploying to a local pypi server.

"""

__docformat__ = 'restructuredtext en'

import os

from pxssh import pxssh

from herring.herring_app import task, run, HerringFile
from herring.support.simple_logger import info
from herringlib.runner import system
from herringlib.version import bump


# pylint: disable=W0604,E0602
global Project

# cleaning is necessary to remove stale .pyc files, particularly after
# refactoring.
@task(depends=['doc_post_clean'])
def build():
    """ build the project as a source distribution """
    if Project.version == '0.0.0':
        bump()
    system("python setup.py sdist")
    # run("python setup.py bdist")


@task(depends=['build'])
def install():
    """ install the project """
    system("python setup.py install --record install.record")


@task()
def uninstall():
    """ uninstall the project"""
    if os.path.exists('install.record'):
        system("cat install.record | xargs rm -rf")
        os.remove('install.record')
    else:
        # try uninstalling with pip
        run(['pip', 'uninstall', HerringFile.directory.split(os.path.sep)[-1]])


@task()
def deploy():
    """ copy latest sdist tar ball to server """
    version = Project.version
    project_version_name = "{name}-{version}.tar.gz".format(name=Project.name, version=version)
    project_latest_name = "{name}-latest.tar.gz".format(name=Project.name)

    pypi_dir = Project.pypiDir
    dist_host = Project.distHost
    dist_dir = '{dir}/{name}'.format(dir=pypi_dir, name=Project.name)
    dist_url = '{host}:/{path}'.format(host=dist_host, path=dist_dir)
    dist_version = '{dir}/{file}'.format(dir=dist_dir, file=project_version_name)
    dist_latest = '{dir}/{file}'.format(dir=dist_dir, file=project_latest_name)
    dist_file = os.path.join(HerringFile.directory, 'dist', project_version_name)

    ssh = pxssh()
    ssh.login(dist_host, Project.user)
    ssh.sendline('mkdir -p {dir}'.format(dir=dist_dir))
    ssh.prompt()
    info(ssh.before)
    ssh.sendline('rm {path}'.format(path=dist_latest))
    ssh.prompt()
    info(ssh.before)
    ssh.logout()

    run(['scp', dist_file, dist_url])

    ssh = pxssh()
    ssh.login(dist_host, Project.user)
    ssh.sendline('ln -s {src} {dest}'.format(src=dist_version, dest=dist_latest))
    ssh.prompt()
    ssh.logout()
