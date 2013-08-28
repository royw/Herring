# coding=utf-8

"""
The command line interface for the herring application.
"""

__docformat__ = 'restructuredtext en'

import argparse
import os
import re
import sys
import textwrap
from herring.argument_helper import ArgumentHelper
from herring.new_project import NewProject
from herring.support.simple_logger import info, Logger
from herring.task_with_args import TaskWithArgs

VERSION_REGEX = r'__version__\s*=\s*[\'\"](\S+)[\'\"]'
ROW_FORMAT = "{0:<{width1}s}  # {1:<{width2}s}"

HELP = {
    'herring': textwrap.dedent("""\
        "Then, you must cut down the mightiest tree in the forrest... with... a herring!"

        Herring is a simple python make utility.  You write tasks in python, and
        optionally assign dependent tasks.  The command line interface lets you
        easily list the tasks and run them.  See --longhelp for details.
        """),
    'herringfile': 'The herringfile to use, by default uses "herringfile".',
    'list_tasks': 'Lists the tasks (with docstrings) in the herringfile.',
    'list_task_usages': 'Shows the full docstring for the tasks (with docstrings) in the herringfile.',
    'list_dependencies': 'Lists the tasks (with docstrings) with their '
                         'dependencies in the herringfile.',
    'list_all_tasks': 'Lists all tasks, even those without docstrings.',
    'version': "Show herring's version.",
    'tasks': "The tasks to run.  If none specified, tries to run the "
             "'default' task.",
    'init': "Initialize a new project to use Herring.  Creates herringfile and herringlib in the given directory.",
    'quiet': 'Suppress herring output.',
    'debug': 'Display debug messages'
}


class HerringCLI(object):
    """Command Line Interface for the Herring App"""

    def execute(self, app):
        """
        Handle the command line arguments then execute the app

        :param app: the herring app instance
        :type app: herring.HerringApp
        """
        settings = self.setup()
        app.execute(self, settings)

    def _get_settings(self):
        """
        Handle the command line arguments

        :return: ArgumentParser instance
        """
        parser = argparse.ArgumentParser('Herring',
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         description=HELP['herring'])
        parser.add_argument('-f', '--herringfile', metavar='FILESPEC',
                            default='herringfile', help=HELP['herringfile'])
        parser.add_argument('-T', '--tasks', dest='list_tasks',
                            action="store_true", help=HELP['list_tasks'])
        parser.add_argument('-U', '--usage', dest='list_task_usages',
                            action="store_true", help=HELP['list_task_usages'])
        parser.add_argument('-D', '--depends', dest='list_dependencies',
                            action="store_true", help=HELP['list_dependencies'])
        parser.add_argument('-a', '--all', dest='list_all_tasks',
                            action='store_true', help=HELP['list_all_tasks'])
        parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                            help=HELP['quiet'])
        parser.add_argument('-d', '--debug', dest='debug',
                            action='store_true', help=HELP['debug'])
        parser.add_argument('-v', '--version', dest='version',
                            action='store_true', help=HELP['version'])
        parser.add_argument('-l', '--longhelp', dest='longhelp', action='store_true',
                            help='Long help about Herring')
        parser.add_argument('-i', '--init', metavar='DIRSPEC',
                            default=None, help=HELP['init'])
        parser.add_argument('tasks', nargs='*', help=HELP['tasks'])
        return parser.parse_known_args()

    def setup(self):
        """
        Command Line Interface.

        Exits the application in the following conditions:

            * user requested the applications version
            * can not find the herringfile

        :return: None
        """

        settings, argv = self._get_settings()

        Logger.setVerbose(not settings.quiet)
        Logger.setDebug(settings.debug)

        TaskWithArgs.argv = argv
        TaskWithArgs.kwargs = ArgumentHelper.argv_to_dict(argv)

        if settings.longhelp:
            info(sys.modules['herring'].__doc__)
            exit(0)

        if settings.version:
            info("Herring version %s" % self._load_version())
            exit(0)

        if settings.init:
            exit(NewProject(settings.init).populate())

        return settings

    def _load_version(self):
        r"""
        Get the version from __init__.py with a line::

            /^__version__\s*=\s*(\S+)/

        If it doesn't exist try to load it from the VERSION.txt file.

        If still no joy, then return '0.0.0'

        :returns: the version string or 'Unknown'
        :rtype: str
        """

        path = os.path.dirname(__file__)

        # trying __init__.py first
        try:
            file_name = os.path.join(path, '__init__.py')
            with open(file_name, 'r') as in_file:
                for line in in_file.readlines():
                    match = re.match(VERSION_REGEX, line)
                    if match:
                        return match.group(1)
        except IOError:
            pass

        # no joy, so try getting the version from a VERSION.txt file.
        try:
            # noinspection PyUnresolvedReferences
            file_name = os.path.join(path, 'VERSION.txt')
            with open(file_name, 'r') as in_file:
                return in_file.read().strip()
        except IOError:
            pass

        # no joy again, so return default
        return 'Unknown'

    def show_tasks(self, tasks):
        """
        Shows the tasks.

        :param tasks: generator for list of task names to show.
         :type tasks: iterator
        :return: None
        """
        self._header("Show tasks")
        for name, description, dependencies, width in tasks:
            self._row(name=name, description=description.strip().splitlines()[0], max_name_length=width)

    def show_task_usages(self, tasks):
        """
        Shows the tasks.

        :param tasks: generator for list of task names to show.
         :type tasks: iterator
        :return: None
        """
        self._header("Show task usages")
        for name, description, dependencies, width in tasks:
            info("#" * 40)
            info("# herring %s" % name)
            info(textwrap.dedent(description).replace("\n\n", "\n").strip())
            info('')

    def show_depends(self, tasks):
        """
        Shows the tasks and their dependencies.

        :param tasks: generator for list of task names to show.
         :type tasks: iterator
        :return: None
        """
        self._header("Show tasks and their dependencies")
        for name, description, dependencies, width in tasks:
            self._row(name=name, description=description.strip().splitlines()[0], dependencies=dependencies, max_name_length=width)

    def _header(self, message):
        """
        Output table header message followed by a horizontal rule.

        :param message: the table header text
         :type message: str
        :return: None
        """
        info(message)
        info("=" * 80)

    def _row(self, name=None, description=None, dependencies=None,
             max_name_length=20):
        """
        Output table row message.

        :param name: the task name
         :type name: str
        :param description: the task description
         :type description: str
        :param dependencies: the task's dependencies
         :type dependencies: list or str
        :param max_name_length: the length of the longest task name in the table
         :type max_name_length: int
        :return: None
        """
        if description is None:
            description = ''
        if dependencies is None:
            dependencies = []

        c1_width = max_name_length + 8
        c2_width = 80 - 5 - c1_width

        self._row_list('herring ' + name, description, c1_width, c2_width)
        if dependencies:
            self._row_list('', 'depends: ' + repr(dependencies), c1_width, c2_width)

    def _row_list(self, c1_value, c2_value, c1_width, c2_width):
        """
        Output the two columns in the table row.

        :param c1_value: value for first column
         :type c1_value: str
        :param c2_value: value for second column
         :type c2_value: str
        :param c1_width: width (number of characters) for first column
         :type c1_width: int
        :param c2_width: width (number of characters) for second column
         :type c2_width: int
        :return: None
        """
        # values = textwrap.fill(self._unindent(c2_value), c2_width).split("\n")
        values = textwrap.fill(c2_value, c2_width).split("\n")
        info(ROW_FORMAT.format(c1_value, values[0], width1=c1_width, width2=c2_width))
        for line in values[1:]:
            info(ROW_FORMAT.format(' ', line, width1=c1_width, width2=c2_width))
