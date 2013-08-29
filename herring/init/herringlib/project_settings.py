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

__docformat__ = 'restructuredtext en'

import fnmatch
import os
import re
import shutil
from herring.herring_app import HerringFile, task
from herring.support.simple_logger import debug, info, error

__author__ = 'wrighroy'

if HerringFile.packagesRequired(['ordereddict']):
    from herringlib.list_helper import compressList, uniqueList

    class ProjectSettings(object):
        """
        Dynamically creates attributes.

        @DynamicAttrs
        """

        def metadata(self, data_dict):
            """
            Set the project's environment attributes

            :param data_dict: the project's attributes
             :type data_dict: dict
            """
            debug("metadata(%s)" % repr(data_dict))
            for key, value in data_dict.items():
                self.__setattr__(key, value)
            required = {'name': 'ProjectName',
                        'package': 'package',
                        'author': 'Author Name',
                        'author_email': 'author@example.com',
                        'description': 'Describe the project here.'}
            for key in required:
                if key not in self.__dict__:
                    self.__setattr__(key, required[key])

        def dirMap(self, dir_dict):
            """
            Set the project's directory structure

            The dirDict keys are appended with a 'Dir' suffix to form attribute names while
            the dirDict values are project root relative paths to the directories.

            :param dir_dict: the project's directory attributes
             :type dir_dict: dict
            """
            debug("dirMap(%s)" % repr(dir_dict))
            for key, value in dir_dict.items():
                self.__setattr__(key + 'Dir', self.__directory(value))

        def __directory(self, relative_name):
            """return the full path from the given path relative to the herringfile directory"""
            directory_name = os.path.join(HerringFile.directory, relative_name)
            return self.__makedirs(directory_name)

        def __makedirs(self, directory_name):
            """mkdir -p"""
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

            for root_dir, dirs, files in os.walk(template_dir):
                for file_name in files:
                    template_filename = os.path.join(root_dir, file_name)
                    # info('template_filename: %s' % template_filename)
                    dest_filename = template_filename.replace('/herringlib/templates/', '/')
                    # info('dest_filename: %s' % dest_filename)
                    if os.path.isdir(template_filename):
                        self.__makedirs(template_filename)
                    else:
                        self.__makedirs(os.path.dirname(dest_filename))
                        root, ext = os.path.splitext(dest_filename)
                        # info('root: %s' % root)
                        if ext == '.template':
                            if not os.path.exists(root):
                                self.__createFromTemplate(template_filename, root)
                        else:
                            if not os.path.exists(dest_filename):
                                shutil.copyfile(template_filename, dest_filename)

        def __createFromTemplate(self, src_filename, dest_filename):
            """
            render the destination file from the source template file

            :param src_filename: the template file
            :param dest_filename: the rendered file
            """
            name = self.__getattribute__('name')
            package = self.__getattribute__('package')
            author = self.__getattribute__('author')
            author_email = self.__getattribute__('author_email')
            description = self.__getattribute__('description')
            with open(src_filename, "r") as in_file:
                template = in_file.read()
                with open(dest_filename, 'w') as out_file:
                    try:
                        out_file.write(template.format(name=name,
                                                       package=package,
                                                       author=author,
                                                       author_email=author_email,
                                                       description=description))
                    # catching all exceptions
                    # pylint: disable=W0703
                    except Exception as ex:
                        error(ex)
    def get_module_docstring(file_path):
        """
        Get module-level docstring of Python module at filepath, e.g. 'path/to/file.py'.
        :param file_path:  The filepath to a module file.
        :type: str
        :returns: the module docstring
        :rtype: str
        """

        comp = compile(open(file_path).read(), file_path, 'exec')
        if comp.co_consts and isinstance(comp.co_consts[0], basestring):
            docstring = comp.co_consts[0]
        else:
            docstring = None
        return docstring


    def getRequirements(doc_string):
        """
        Extract the required packages from the docstring.

        This makes the following assumptions:

        1) there is a line in the docstring that contains "requirements.txt"
        2) after that line, ignoring blank lines, there are bullet list items starting with a '*'
        3) these bullet list items are the names of the required third party packages

        :param doc_string: a module docstring
        :type: str
        """
        if doc_string is None:
            return []
        requirements = []
        contiguous = False
        for line in compressList(doc_string.split("\n")):
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

        requirements_filename = os.path.join(HerringFile.directory, 'requirements.txt')
        if not os.path.exists(requirements_filename):
            info("Missing: " + requirements_filename)
            return

        with open(requirements_filename, 'r') as in_file:
            requirements = [re.split("<|>|=|!", line)[0] for line in [line.strip() for line in in_file.readlines()]
                            if line and not line.startswith('#')]
            required = sorted(compressList(uniqueList(requirements)))

        diff = sorted(set(needed) - set(required))
        if not diff:
            info("Your %s includes all known herringlib task requirements" % requirements_filename)
            return

        info("Please add the following to your %s:\n" % requirements_filename)
        info("\n".join(diff))
