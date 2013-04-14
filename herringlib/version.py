import os
from herring.herring_app import task


def getProjectVersion(project_package=None):
    """ get the version from VERSION.txt """
    try:
        version_file = os.path.join(os.getcwd(), project_package, 'VERSION.txt')
        print "version_file => %s" % version_file
        with open(version_file, 'r') as file_:
            return file_.read().strip()
    except IOError:
        pass
    return '0.0.0'


def setProjectVersion(version, project_package=None):
    """ set the version in VERSION.txt """
    try:
        version_file = os.path.join(os.getcwd(), project_package, 'VERSION.txt')
        with open(version_file, 'w') as f:
            f.write(version + "\n")
    except IOError as e:
        print str(e)


@task()
def bump():
    """
    Bumps the patch version in VERSION file up by one.  If the VERSION
    file does not exist, then create it and initialize the version to '0.0.0'.
    """
    version = getProjectVersion()
    parts = version.split('.')
    parts[-1] = str(int(parts[-1]) + 1)
    setProjectVersion('.'.join(parts))
    print "Bumped version from %s to %s" % (version, getProjectVersion())


