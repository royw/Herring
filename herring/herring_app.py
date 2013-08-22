# coding=utf-8

"""
The main Herring application.
"""

from herring.herring_file import HerringFile
from herring.task_with_args import TaskWithArgs, HerringTasks

__docformat__ = "restructuredtext en"

import fnmatch
from operator import itemgetter
import textwrap

import re
import os
import sys

from herring.support.toposort2 import toposort2
from herring.support.SimpleLogger import debug, info, error, fatal, setVerbose, setDebug


__all__ = ("HerringApp", "task", "run", "HerringTasks")


ROW_FORMAT = "{0:<{width1}s}  # {1:<{width2}s}"

# Alias for task decorator just makes the herringfiles a little cleaner.
task = TaskWithArgs
run = HerringFile.run


class HerringApp(object):
    """
    This is the application class.

    Usage:
        herring = Herring(outputter=sys.stdout)
        herring.cli()
        herring.execute()
    """

    def __init__(self):
        """
        The Herring application.
        """
        # noinspection PyArgumentEqualDefault
        setVerbose(True)
        setDebug(False)

    def execute(self, settings):
        """
        Execute the tasks specified in the _settings object.

        Currently:
            * settings.list_task asserted shows the available tasks.
            * settings.list_dependencies asserted shows the available tasks
                and their dependencies.
            * settings.list_all_tasks asserted modifies the listing to include
                tasks that do not have a docstring.
            * if both settings.list_task and settings.list_dependencies are
                deasserted, then run the tasks from settings.tasks
        :param settings: the application settings

        :return: None
        """
        try:
            herring_file = self._find_herring_file(settings.herringfile)
            HerringFile.directory = str(os.path.realpath(os.path.dirname(herring_file)))
            sys.path.insert(1, HerringFile.directory)

            # the tasks are always ran with the current working directory
            # set to the directory that contains the herringfile
            os.chdir(HerringFile.directory)

            info("Using: %s" % herring_file)

            self._load_tasks(herring_file)
            task_list = list(self._get_tasks_list(HerringTasks,
                                                  settings.list_all_tasks))
            if settings.list_tasks:
                self._show_tasks(task_list)
            elif settings.list_task_usages:
                self._show_task_usages(task_list)
            elif settings.list_dependencies:
                self._show_depends(task_list)
            else:
                try:
                    self._run_tasks(settings.tasks)
                except ValueError as ex:
                    fatal(ex)
        except ValueError as ex:
            fatal(ex)

    def _find_herring_file(self, herringfile):
        """
        Tries to locate the herringfile in the current directory, if not found
        then tries the parent directory, repeat until either found or the root
        is hit.

        :param herringfile: the base file name for the herringfile
        :return: the filespec to the found herringfile
        :raises ValueError: if unable to find the herringfile
        """
        cwd = os.getcwd()
        while cwd:
            try:
                file_spec = os.path.join(cwd, herringfile)
                with open(file_spec):
                    pass
                return file_spec
            except IOError:
                cwd = os.sep.join(cwd.split(os.sep)[0:-1])
        raise ValueError("Unable to find %s" % herringfile)

    def _load_tasks(self, herring_file):
        """
        Loads any herringlib files then loads the given herringfile.

        :param herring_file: the herringfile
        :return: None
        """
        self._load_herring_file(herring_file)
        for file_ in self.library_files(herring_file):
            self._load_herring_file(file_)

    @staticmethod
    def library_files(herring_file, lib_base_name='herringlib',
                      pattern='*.py'):
        """
        yield any .herring files located in herringlib subdirectory in the
        same directory as the given herringfile.  Ignore package __init__.py
        files.

        :param herring_file: the herringfile
        :param lib_base_name: the base name of the library relative to the
            directory where the herring_file is located
        :param pattern: the file pattern (glob) to select
        :yield: path to a library herring file
        :return: None
        """
        lib_dir = os.path.join(os.path.dirname(herring_file), lib_base_name)
        if os.path.isdir(lib_dir):
            files = [os.path.join(root, f)
                     for root, dirs, files in os.walk(lib_dir)
                     for d in dirs if not re.match(r'/templates/', d)
                     for f in fnmatch.filter(files, pattern)]
            for file_name in files:
                if os.path.basename(file_name) == '__init__.py':
                    continue
                debug("loading herringlib:  %s" % file_name)
                yield file_name

    def _load_herring_file(self, herring_file):
        """
        Loads the tasks from the herringfile populating the
        HerringApp.HerringTasks structure.

        :param herring_file: the herringfile
        :return: None
        """
        with open(str(herring_file)) as file_:
            dest_lines = [line
                          for line in file_.readlines()
                          if not re.match(r"""
                                           ^\s*
                                           (
                                                from\s+herring\.herring_app
                                              | import\s+herring
                                           )
                                           """, line, re.VERBOSE)]
            herring_source = "\n".join(dest_lines)
            try:
                # run = HerringFile.run
                locals_ = locals()
                globals_ = globals()
                exec(herring_source, globals_)
            except ImportError as ex:
                error(ex)

    def _get_tasks_list(self, herring_tasks, all_tasks_flag):
        """
        massage the tasks structure into an easier to access dict

        :param herring_tasks: the herring task structure
        :param all_tasks_flag: asserted to include all tasks, deasserted to
            only include tasks with a docstring
        :returns: task_list, a dict {name: '...', description: '...',
            dependencies: ['...']
        """
        for task_name in herring_tasks.keys():
            description = herring_tasks[task_name]['description']
            if all_tasks_flag or description is not None:
                yield({'name': task_name,
                       'description': str(description),
                       'dependencies': herring_tasks[task_name]['depends']})

    def _show_tasks(self, task_list):
        """
        Shows the tasks.

        :param task_list: list of task names to show.
        :return: None
        """
        self._header("Show tasks")
        width = len(max([item['name'] for item in task_list], key=len))
        for item in sorted(task_list, key=itemgetter('name')):
            self._row(name=item['name'],
                      description=item['description'].strip().splitlines()[0],
                      max_name_length=width)

    def _show_task_usages(self, task_list):
        """
        Shows the tasks.

        :param task_list: list of task names to show.
        :return: None
        """
        self._header("Show task usages")
        for item in sorted(task_list, key=itemgetter('name')):
            info("#" * 40)
            info("# herring %s" % item['name'])
            info(textwrap.dedent(item['description']).replace("\n\n", "\n").strip())
            info('')

    def _show_depends(self, task_list):
        """
        Shows the tasks and their dependencies.

        :param task_list: list of task names to show.
        :return: None
        """
        self._header("Show tasks and their dependencies")
        width = len(max([item['name'] for item in task_list], key=len))
        for item in sorted(task_list, key=itemgetter('name')):
            self._row(name=item['name'],
                      description=item['description'].strip().splitlines()[0],
                      dependencies=item['dependencies'],
                      max_name_length=width)

    def _get_default_tasks(self):
        """
        Get a list of default task names (@task(default=True))

        :return: List containing default task names.
        """
        if 'default' in HerringTasks.keys():
            return ['default']
        return []

    def _verify_tasks_exists(self, task_list):
        """
        If a given task does not exist, then raise a ValueError exception

        :return: None
        :raises ValueError:
        """
        if not task_list:
            task_list = self._get_default_tasks()
        if not task_list:
            raise ValueError("No tasks given")
        for name in task_list:
            task_names = HerringTasks.keys()
            if name not in task_names:
                raise ValueError("Unable to find task: '%s'. "
                                 "Available tasks: %s" %
                                 (name, str(task_names)))
        return task_list

    def _tasks_to_depend_dict(self, src_tasks, herring_tasks):
        """
        builds dictionary used by toposort2 from HerringTasks

        :param src_tasks: a List of task names
        :param herring_tasks: list of tasks from the herringfile
        :return: dict where key is task name and value is List of dependency
            task names
        """
        data = {}
        for name in src_tasks:
            data[name] = set(herring_tasks[name]['depends'])
        return data

    def _find_dependencies(self, src_tasks, herring_tasks):
        """
        finds the dependent tasks for the given source tasks, building up an
        unordered list of tasks

        :param src_tasks: list of task names that may have dependencies
        :param herring_tasks: list of tasks from the herringfile
        :return: list of resolved (including dependencies) task names
        """
        dependencies = []
        for name in src_tasks:
            dependencies.append(name)
            tasks = self._find_dependencies(herring_tasks[name]['depends'],
                                            herring_tasks)
            dependencies.extend(tasks)
        return dependencies

    def _resolve_dependencies(self, src_tasks, herring_tasks):
        """
        resolve the dependencies for the given list of task names

        :param src_tasks: list of task names that may have dependencies
        :param herring_tasks: list of tasks from the herringfile
        :return: list of resolved (including dependencies) task names
        """
        tasks = self._find_dependencies(src_tasks, herring_tasks)
        task_list = []
        depend_dict = self._tasks_to_depend_dict(tasks, herring_tasks)
        for task_group in toposort2(depend_dict):
            task_list.extend(list(task_group))
        return task_list

    def _run_tasks(self, task_list):
        """
        Runs the tasks given on the command line.

        :param task_list: the list of task names to run
        :return: None
        """
        verified_task_list = self._verify_tasks_exists(task_list)
        for task_name in self._resolve_dependencies(verified_task_list,
                                                    HerringTasks):
            info("Running: %s" % task_name)
            HerringTasks[task_name]['task']()

    def _header(self, message):
        """
        Output table header message followed by a horizontal rule.

        :param message: the table header text
        :return: None
        """
        info(message)
        info("=" * 80)

    def _row(self, name=None, description=None, dependencies=None,
             max_name_length=20):
        """
        Output table row message.

        :param name: the task name
        :param description: the task description
        :param dependencies: the task's dependencies
        :param max_name_length: the length of the longest task name in the table
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
        :param c2_value: value for second column
        :param c1_width: width (number of characters) for first column
        :param c2_width: width (number of characters) for second column
        :return: None
        """
        # values = textwrap.fill(self._unindent(c2_value), c2_width).split("\n")
        values = textwrap.fill(c2_value, c2_width).split("\n")
        info(ROW_FORMAT.format(c1_value, values[0], width1=c1_width, width2=c2_width))
        for line in values[1:]:
            info(ROW_FORMAT.format(' ', line, width1=c1_width, width2=c2_width))
