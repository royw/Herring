import fnmatch
import os
import re
import shutil
from herring.herring_app import HerringFile, task
import sys
from herring.support.SimpleLogger import debug, info, error
from herringlib.list_helper import compressList, uniqueList

__author__ = 'wrighroy'


class ProjectSettings(object):
    """
    Dynamically creates attributes.

    @DynamicAttrs
    """

    def metadata(self, dataDict):
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
    """Get module-level docstring of Python module at filepath, e.g. 'path/to/file.py'."""

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
