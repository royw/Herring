# coding=utf-8

"""
The command line interface for the herring application.
"""

import io
import os
import re
import sys
import textwrap
import json

from pprint import pformat

from herring.herring_settings import HerringSettings
from herring.support.terminalsize import get_terminal_size
from herring.argument_helper import ArgumentHelper
from herring.support.simple_logger import info, Logger
from herring.task_with_args import TaskWithArgs

__docformat__ = 'restructuredtext en'

VERSION_REGEX = r'__version__\s*=\s*[\'\"](\S+)[\'\"]'
ROW_FORMAT = "{0:<{width1}s}  # {1:<{width2}s}"


# noinspection PyMethodMayBeStatic,PyArgumentEqualDefault
class HerringCLI(object):
    """Command Line Interface for the Herring App"""

    def execute(self, app):
        """
        Handle the command line arguments then execute the app.

        :param app: the herring app instance
        :type app: herring.HerringApp
        """
        settings = self.setup()
        app.execute(self, settings)

    def setup(self):
        """
        Command Line Interface.

        Exits the application in the following conditions:

            * user requested the applications version,
            * user requested help or longhelp,
            * can not find the herringfile.

        :return: None
        """

        parser, settings, argv = HerringSettings().parse()

        Logger.set_verbose(not settings.quiet)
        Logger.set_debug(settings.herring_debug)

        TaskWithArgs.argv = argv
        TaskWithArgs.kwargs = ArgumentHelper.argv_to_dict(argv)

        if settings.longhelp:
            info(sys.modules['herring'].__doc__)
            exit(0)

        if settings.version:
            info("Herring version %s" % self._load_version())
            exit(0)

        return settings

    def _load_version(self, path=None):
        r"""
        Get the version from __init__.py with a line::

            /^__version__\s*=\s*(\S+)/

        If it doesn't exist try to load it from the VERSION.txt file.

        If still no joy, then return '0.0.0'

        :returns: the version string or 'Unknown'
        :rtype: str
        """

        if path is None:
            path = os.path.dirname(__file__)

        # trying __init__.py first
        try:
            file_name = os.path.join(path, '__init__.py')
            # noinspection PyBroadException
            with io.open(file_name, 'r', encoding='utf-8') as inFile:
                for line in inFile.readlines():
                    match = re.match(VERSION_REGEX, line)
                    if match:
                        return match.group(1)
        except IOError:
            pass

        # no joy again, so return default
        return 'Unknown'

    def show_environment(self):
        """Show the runtime environment for herring"""
        info('os.environ: {data}'.format(data=pformat(os.environ)))
        info('sys.argv: {data}'.format(data=pformat(sys.argv)))
        info('sys.executable: {data}'.format(data=pformat(sys.executable)))
        info('sys.path: {data}'.format(data=pformat(sys.path)))
        info('sys.platform: {data}'.format(data=pformat(sys.platform)))
        info('sys.version_info: {data}'.format(data=pformat(sys.version_info)))

    def show_tasks(self, tasks, herring_tasks, settings):
        """
        Shows the tasks.

        :param tasks: generator for list of task names to show.
        :type tasks: iterator
        :param herring_tasks: all of the herring tasks
        :type herring_tasks: dict
        :param settings: the application settings
        :return: None
        """
        if settings.json:
            info('[')
            for name, description, dependencies, dependent_of, kwargs, arg_prompt, width in tasks:
                info(json.dumps({'name': name,
                                 'description': description,
                                 'dependencies': dependencies,
                                 'dependent_of': dependent_of,
                                 'kwargs': kwargs,
                                 'arg_prompt': arg_prompt}))
            info(']')
        else:
            self._header("Show tasks")
            for name, description, dependencies, dependent_of, kwargs, arg_prompt, width in tasks:
                self._row(name=name, description=description.strip().splitlines()[0], max_name_length=width)
            self._footer(herring_tasks)

    def show_task_usages(self, tasks, herring_tasks, settings):
        """
        Shows the tasks.

        :param tasks: generator for list of task names to show.
        :type tasks: iterator
        :param herring_tasks: all of the herring tasks
        :type herring_tasks: dict
        :param settings: the application settings
        :return: None
        """
        if settings.json:
            info('[')
            for name, description, dependencies, dependent_of, kwargs, arg_prompt, width in tasks:
                info(json.dumps({'name': name,
                                 'description': description,
                                 'dependencies': dependencies,
                                 'dependent_of': dependent_of,
                                 'kwargs': kwargs,
                                 'arg_prompt': arg_prompt}))
            info(']')
        else:
            self._header("Show task usages")
            for name, description, dependencies, dependent_of, kwargs, arg_prompt, width in tasks:
                info("#" * 40)
                info("# herring %s" % name)
                info(textwrap.dedent(description).replace("\n\n", "\n").strip())
                info('')
            self._footer(herring_tasks)

    def show_depends(self, tasks, herring_tasks, settings):
        """
        Shows the tasks and their dependencies.

        :param tasks: generator for list of task names to show.
        :type tasks: iterator
        :param herring_tasks: all of the herring tasks
        :type herring_tasks: dict
        :param settings: the application settings
        :return: None
        """
        if settings.json:
            info('[')
            for name, description, dependencies, dependent_of, kwargs, arg_prompt, width in tasks:
                info(json.dumps({'name': name,
                                 'description': description,
                                 'dependencies': dependencies,
                                 'dependent_of': dependent_of,
                                 'kwargs': kwargs,
                                 'arg_prompt': arg_prompt}))
            info(']')
        else:
            self._header("Show tasks and their dependencies")
            for name, description, dependencies, dependent_of, kwargs, arg_prompt, width in tasks:
                self._row(name=name,
                          description=description.strip().splitlines()[0],
                          dependencies=dependencies,
                          dependent_of=dependent_of,
                          max_name_length=width)
            self._footer(herring_tasks)

    def _header(self, message):
        """
        Output table header message followed by a horizontal rule.

        :param message: the table header text
         :type message: str
        :return: None
        """
        (console_width, console_height) = get_terminal_size()
        info(message)
        info("=" * console_width)

    def _footer(self, tasks):
        tasks_help = []
        for task_name in tasks:
            task = tasks[task_name]
            if task['help']:
                tasks_help.append("{name}:  {help}".format(name=task_name, help=task['help']))
        if tasks_help:
            info('')
            info('Notes:')
            info("\n".join(tasks_help))

    def _row(self, name=None, description=None, dependencies=None, dependent_of=None,
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

        (console_width, console_height) = get_terminal_size()

        c1_width = max_name_length + 8
        c2_width = console_width - 5 - c1_width

        self._row_list('herring ' + name, description, c1_width, c2_width)
        if dependencies:
            self._row_list('', 'depends: ' + repr(dependencies), c1_width, c2_width)
        if dependent_of is not None:
            self._row_list('', 'dependent_of: ' + dependent_of, c1_width, c2_width)

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
