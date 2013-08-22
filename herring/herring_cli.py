# coding=utf-8

"""
The command line interface for the herring application.
"""

import argparse
import os
import re
import sys
import textwrap
from herring.argument_helper import ArgumentHelper
from herring.new_project import NewProject
from herring.support.SimpleLogger import setVerbose, setDebug, info
from herring.task_with_args import TaskWithArgs

VERSION_REGEX = r'__version__\s*=\s*[\'\"](\S+)[\'\"]'

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
        :type app: HerringApp
        """
        settings = self.cli()
        app.execute(settings)

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

    def cli(self):
        """
        Command Line Interface.

        Exits the application in the following conditions:
        * user requested the applications version
        * can not find the herringfile

        :return: None
        """

        settings, argv = self._get_settings()

        setVerbose(not settings.quiet)
        setDebug(settings.debug)

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
        """
        Get the version from __init__.py with a line: /^__version__\s*=\s*(\S+)/
        If it doesn't exist try to load it from the VERSION.txt file.
        If still no joy, then return '0.0.0'

        :returns: the version string or 'Unknown'
        :rtype: str
        """

        path = os.path.dirname(__file__)

        # trying __init__.py first
        try:
            file_name = os.path.join(path, '__init__.py')
            with open(file_name, 'r') as inFile:
                for line in inFile.readlines():
                    match = re.match(VERSION_REGEX, line)
                    if match:
                        return match.group(1)
        except IOError:
            pass

        # no joy, so try getting the version from a VERSION.txt file.
        try:
            # noinspection PyUnresolvedReferences
            file_name = os.path.join(path, 'VERSION.txt')
            with open(file_name, 'r') as inFile:
                return inFile.read().strip()
        except IOError:
            pass

        # no joy again, so return default
        return 'Unknown'
