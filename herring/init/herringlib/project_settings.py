# coding=utf-8

"""
Handle the project's environment to support the generic tasks.

Each project must define it's metadata and directory structure.  This is usually done in the project's herringfile.

.. code-block: python

    Project = ProjectSettings()

    Project.metadata(
        {
            'name': 'Herring',
            'package': 'herring',
            'author': 'Roy Wright',
            'author_email': 'roy.wright@hp.com',
            'description': '',
            'script': 'herring',
            'main': 'herring_app.py',
            'version': version,
            'distHost': 'tpcvm143.austin.hp.com',
            'pypiDir': '/var/pypi/dev',
            'user': os.environ['USER'],
            'pylintrc': os.path.join(HerringFile.directory, 'pylint.rc'),
            'pythonPath': ".:%s" % HerringFile.directory
        })

    Project.dirMap(
        {
            'quality': 'quality',
            'docs': 'docs',
            'uml': 'docs/_src/uml',
            'api': 'docs/api',
            'templates': 'docs/_templates',
            'report': 'report',
            'tests': 'tests',
            'dist': 'dist',
            'build': 'build',
            'egg': "%s.egg-info" % Project.name
        }
    )

Inside *herringlib* is a *templates* directory.  Calling *Project.requiredFiles()* will render
these template files and directories into the project root, if the file does not exist in the project
root (files will NOT be overwritten).  Files ending in .template are string templates that are rendered
by invoking *.format(name, package, author, author_email, description)*. Other files will simply be
copied as is.

It is recommended to call *Project.requiredFiles()* in your *herringfile*.

Herringlib's generic tasks will define a comment in the module docstring similar to the following
that declares external dependencies::

    Add the following to your *requirements.txt* file:

    * cheesecake
    * matplotlib
    * numpy
    * pycabehtml
    * pylint
    * pymetrics

Basically a line with "requirements.txt" followed by a list is assumed to identify these dependencies by
the *checkRequirements()* task.

Tasks may access the project attributes with:

.. code-block:

    global Project

    print("Project Name: %s" % Project.name)

Project directories are accessed using a 'Dir' suffix.  For example the 'docs' directory would be accessed
with *Project.docsDir*.

"""

import fnmatch
import os
import re
import shutil
from herring.herring_app import HerringFile, task
from herring.support.SimpleLogger import debug, info, error
from herringlib.list_helper import compressList, uniqueList

__author__ = 'wrighroy'


class ProjectSettings(object):
    """
    Dynamically creates attributes.

    @DynamicAttrs
    """

    def metadata(self, dataDict):
        """
        Set the project's environment attributes

        :param dataDict: the project's attributes
         :type dataDict: dict
        """
        debug("metadata(%s)" % repr(dataDict))
        for key, value in dataDict.items():
            self.__setattr__(key, value)
        required = {'name': 'ProjectName',
                    'package': 'package',
                    'author': 'Author Name',
                    'author_email': 'author@example.com',
                    'description': 'Describe the project here.'}
        for key in required:
            if key not in self.__dict__:
                self.__setattr__(key, required[key])

    def dirMap(self, dirDict):
        """
        Set the project's directory structure

        The dirDict keys are appended with a 'Dir' suffix to form attribute names while
        the dirDict values are project root relative paths to the directories.

        :param dirDict: the project's directory attributes
         :type dirDict: dict
        """
        debug("dirMap(%s)" % repr(dirDict))
        for key, value in dirDict.items():
            self.__setattr__(key + 'Dir', self.__directory(value))

    def __directory(self, relativeName):
        directory_name = os.path.join(HerringFile.directory, relativeName)
        return self.__makedirs(directory_name)

    def __makedirs(self, directory_name):
        try:
            os.makedirs(directory_name)
        except OSError, err:
            if err.errno != 17:
                raise
        return directory_name

    def requiredFiles(self):
        """
        Create required files.  Note, will not overwrite any files.

        Scans the templates directory and create any corresponding files relative
        to the root directory.  If the file is a .template, then renders the file,
        else simply copy it.

        Template files are just string templates which will be formatted with the
        following named arguments:  name, package, author, author_email, and description.

        Note, be sure to escape curly brackets ('{', '}') with double curly brackets ('{{', '}}').
        """
        debug("requiredFiles")
        template_dir = os.path.abspath(os.path.join(HerringFile.directory, 'herringlib', 'templates'))

        for dirName, dirNames, fileNames in os.walk(template_dir):
            for fileName in fileNames:
                template_filename = os.path.join(dirName, fileName)
                dest_filename = template_filename.replace('/herringlib/templates/', '/')
                if os.path.isdir(template_filename):
                    self.__makedirs(template_filename)
                else:
                    self.__makedirs(os.path.dirname(dest_filename))
                    root, ext = os.path.splitext(dest_filename)
                    if ext == '.template':
                        if not os.path.exists(root):
                            self.__createFromTemplate(template_filename, root)
                    else:
                        if not os.path.exists(dest_filename):
                            shutil.copyfile(template_filename, dest_filename)

    def __createFromTemplate(self, srcFilename, destFilename):
        name = self.__getattribute__('name')
        package = self.__getattribute__('package')
        author = self.__getattribute__('author')
        author_email = self.__getattribute__('author_email')
        description = self.__getattribute__('description')
        with open(srcFilename, "r") as inFile:
            template = inFile.read()
            with open(destFilename, 'w') as outFile:
                try:
                    outFile.write(template.format(name=name,
                                                  package=package,
                                                  author=author,
                                                  author_email=author_email,
                                                  description=description))
                except Exception as ex:
                    error(ex)


def get_module_docstring(filePath):
    """
    Get module-level docstring of Python module at filepath, e.g. 'path/to/file.py'.
    :param filePath:  The filepath to a module file.
    :type: str
    :returns: the module docstring
    :rtype: str
    """

    co = compile(open(filePath).read(), filePath, 'exec')
    if co.co_consts and isinstance(co.co_consts[0], basestring):
        docstring = co.co_consts[0]
    else:
        docstring = None
    return docstring


def getRequirements(docString):
    """
    Extract the required packages from the docstring.

    This makes the following assumptions:

    1) there is a line in the docstring that contains "requirements.txt"
    2) after that line, ignoring blank lines, there are bullet list items starting with a '*'
    3) these bullet list items are the names of the required third party packages

    :param docString: a module docstring
    :type: str
    """
    if docString is None:
        return []
    requirements = []
    contiguous = False
    for line in compressList(docString.split("\n")):
        if 'requirements.txt' in line:
            contiguous = True
            continue
        if contiguous:
            match = re.match(r'\*\s+(\S+)', line)
            if match:
                requirements.append(match.group(1))
            else:
                contiguous = False
    return requirements


@task()
def checkRequirements():
    """Checks that herringfile and herringlib/* required packages are in requirements.txt file"""
    files = [os.path.join(dir_path, f)
             for dir_path, dir_names, files in os.walk(os.path.join(HerringFile.directory, 'herringlib'))
             for f in fnmatch.filter(files, '*.py')]
    files.append(os.path.join(HerringFile.directory, 'herringfile'))
    requirements = []
    for file_ in files:
        requirements += getRequirements(get_module_docstring(file_))
    needed = sorted(compressList(uniqueList(requirements)))

    requirementsFilename = os.path.join(HerringFile.directory, 'requirements.txt')
    if not os.path.exists(requirementsFilename):
        info("Missing: " + requirementsFilename)
        return

    with open(requirementsFilename, 'r') as inFile:
        requirements = [re.split("<|>|=|!", line)[0] for line in [line.strip() for line in inFile.readlines()]
                        if line and not line.startswith('#')]
        required = sorted(compressList(uniqueList(requirements)))

    diff = sorted(set(needed) - set(required))
    if not diff:
        info("Your %s includes all known herringlib task requirements" % requirementsFilename)
        return

    info("Please add the following to your %s:\n" % requirementsFilename)
    info("\n".join(diff))
