# coding=utf-8
"""
Set of Herring tasks for packaging a project.

In early development, the install/uninstall tasks are useful.
Less so after you start deploying to a local pypi server.

"""

import os
from herring.herring_app import task, run, HerringFile
from pxssh import pxssh
from herring.support.SimpleLogger import info
from herringlib.runner import system
from herringlib.version import bump


global Project


# cleaning is necessary to remove stale .pyc files, particularly after
# refactoring.
@task(depends=['doc_post_clean'])
def build():
    """ build the project as a source distribution """
    if Project.version == '0.0.0':
        bump()
    system("python setup.py sdist")
    system("python setup.py bdist_wheel")
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
    projectVersionName = "{name}-{version}.tar.gz".format(name=Project.name, version=version)
    projectLatestName = "{name}-latest.tar.gz".format(name=Project.name)

    pypiDir = Project.pypiDir
    distHost = Project.distHost
    distDir = '{dir}/{name}'.format(dir=pypiDir, name=Project.name)
    distUrl = '{host}:/{path}'.format(host=distHost, path=distDir)
    distVersion = '{dir}/{file}'.format(dir=distDir, file=projectVersionName)
    distLatest = '{dir}/{file}'.format(dir=distDir, file=projectLatestName)
    distFile = os.path.join(HerringFile.directory, 'dist', projectVersionName)

    s = pxssh()
    s.login(distHost, Project.user)
    s.sendline('mkdir -p {dir}'.format(dir=distDir))
    s.prompt()
    info(s.before)
    s.sendline('rm {path}'.format(path=distLatest))
    s.prompt()
    info(s.before)
    s.logout()

    run(['scp', distFile, distUrl])

    s = pxssh()
    s.login(distHost, Project.user)
    s.sendline('ln -s {src} {dest}'.format(src=distVersion, dest=distLatest))
    s.prompt()
    s.logout()


@task()
def updateReadme():
    """Update the README.txt from the application's --longhelp output"""
    text = system("%s --longhelp" % os.path.join(HerringFile.directory, Project.package, Project.main))
    with open("README.txt", 'w') as readme_file:
        readme_file.write(text)


