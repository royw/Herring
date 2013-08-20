import os
from herring.herring_app import task, HerringFile
from herring.support.SimpleLogger import info, error


global Project


def getProjectVersion(project_package=None):
    """ get the version from VERSION.txt """
    try:
        parts = [HerringFile.directory, project_package, 'VERSION.txt']
        version_file = os.path.join(*[f for f in parts if f is not None])
        info("version_file => %s" % version_file)
        with open(version_file, 'r') as file_:
            return file_.read().strip()
    except IOError:
        pass
    return '0.0.0'


def setProjectVersion(version, project_package=None):
    """ set the version in VERSION.txt """
    try:
        parts = [HerringFile.directory, project_package, 'VERSION.txt']
        version_file = os.path.join(*[f for f in parts if f is not None])
        with open(version_file, 'w') as f:
            f.write(version + "\n")
    except IOError as e:
        error(e)


@task()
def bump():
    """
    Bumps the patch version in VERSION file up by one.
    If the VERSION file does not exist, then create it and initialize the version to '0.0.0'.
    """
    version = getProjectVersion(project_package=Project.package)
    parts = version.split('.')
    parts[-1] = str(int(parts[-1]) + 1)
    setProjectVersion('.'.join(parts), project_package=Project.package)
    Project.version = getProjectVersion(project_package=Project.package)
    info("Bumped version from %s to %s" % (version, Project.version))


@task()
def version():
    """Show the current version"""
    info("Current version is: %s" % getProjectVersion(project_package=Project.package))
