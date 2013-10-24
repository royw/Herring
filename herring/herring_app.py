# coding=utf-8

"""
The main Herring application.
"""
from imp import PY_SOURCE
import pkgutil
import types
from unipath import Path

__docformat__ = 'restructuredtext en'

import re
import os
import sys

from operator import itemgetter
from herring.support.toposort2 import toposort2
from herring.support.simple_logger import debug, info, error, fatal, Logger
from herring.herring_file import HerringFile
from herring.support.utils import findFiles
from herring.task_with_args import TaskWithArgs, HerringTasks


__all__ = ("HerringApp", "task", "run", "HerringTasks")

# Alias for task decorator just makes the herringfiles a little cleaner.
# pylint: disable=C0103
task = TaskWithArgs
run = HerringFile.run


class HerringApp(object):
    """
    This is the application class.

    Usage::

        cli = HerringCLI()
        cli.execute(HerringApp())
    """

    def __init__(self):
        """
        The Herring application.
        """
        # noinspection PyArgumentEqualDefault
        Logger.setVerbose(True)
        Logger.setDebug(False)

    def execute(self, cli, settings):
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

        :param cli: the command line interface instance
        :type cli: herring.HerringCLI
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
            task_list = list(self._get_tasks_list(HerringTasks, settings.list_all_tasks))
            if settings.list_tasks:
                cli.show_tasks(self._get_tasks(task_list), HerringTasks)
            elif settings.list_task_usages:
                cli.show_task_usages(self._get_tasks(task_list), HerringTasks)
            elif settings.list_dependencies:
                cli.show_depends(self._get_tasks(task_list), HerringTasks)
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
        :type herringfile: str
        :return: the filespec to the found herringfile
        :rtype: str
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

    def _load_tasks(self, herringfile):
        """
        Loads the given herringfile then loads any herringlib files.

        :param herringfile: the herringfile path
        :type herringfile: str
        :return: None
        """
        sys.path.extend(os.path.dirname(herringfile))
        self._load_file(herringfile)
        for file_name in self.library_files(herringfile):
            debug("file_name = {file}".format(file=file_name))
            mod_name = 'herringlib.' + Path(file_name).stem
            debug("mod_name = {name}".format(name=mod_name))
            __import__(mod_name)


    @staticmethod
    def library_files(herringfile, lib_base_name='herringlib',
                      pattern='*.py'):
        """
        Yield any .herring files located in herringlib subdirectory in the
        same directory as the given herringfile.  Ignore package __init__.py
        files, .svn and templates sub-directories.

        :param herringfile: the herringfile
        :type herringfile: str
        :param lib_base_name: the base name of the library relative to the
            directory where the herring_file is located
        :type lib_base_name: str
        :param pattern: the file pattern (glob) to select
        :type pattern: str
        :return: iterator for path to a library herring file
        :rtype: iterator
        """
        herring_path = Path(os.path.dirname(herringfile))
        lib_dir = Path(herring_path, lib_base_name)
        if lib_dir.isdir():
            files = findFiles(lib_dir, excludes=['*/templates/*', '.svn'], includes=[pattern])
            for file_path in [Path(file_name) for file_name in files]:
                if file_path.name == '__init__.py':
                    continue
                debug("loading from herringlib:  %s" % file_path)
                yield herring_path.rel_path_to(file_path)

    def load_plugin(self, plugin, paths):
        import imp

        # check if we haven't loaded it already
        try:
            return sys.modules[plugin]
        except KeyError:
            pass
        # ok, the load it
        #fp, filename, desc = imp.find_module(plugin, paths)
        filename = os.path.join(paths, plugin)
        extension = os.path.splitext(filename)[1]
        mode = 'r'
        desc = (extension, mode, PY_SOURCE)
        debug(repr(desc))
        with open(filename, mode) as fp:
            mod = imp.load_module(plugin, fp, filename, desc)
        return mod

    def _load_file(self, file_name):
        """
        Loads the tasks from the herringfile populating the
        HerringApp.HerringTasks structure.

        :param file_name: the herringfile
        :type file_name: str
        :return: None
        """
        plugin = os.path.basename(file_name)
        path = os.path.dirname(file_name)
        debug("plugin: {plugin}, path: {path}".format(plugin=plugin, path=path))
        self.load_plugin(plugin, path)

    def _get_tasks_list(self, herring_tasks, all_tasks_flag):
        """
        A generator to massage the tasks structure into an easier to access dict.

        :param herring_tasks: the herring task structure
        :type herring_tasks: dict
        :param all_tasks_flag: asserted to include all tasks, deasserted to
            only include tasks with a docstring
        :type all_tasks_flag: bool
        :returns: a task_list dictionary {name: '...', description: '...',
            dependencies: ['...']
        :rtype: dict
        """
        for task_name in herring_tasks.keys():
            description = herring_tasks[task_name]['description']
            if all_tasks_flag or description is not None:
                yield ({'name': task_name,
                        'description': str(description),
                        'dependencies': herring_tasks[task_name]['depends']})

    def _get_tasks(self, task_list):
        """
        Generator for getting the sorted list of tasks with descriptions and dependencies
        for show tasks features.

        :param task_list: list of task names to show.
        :type task_list: list
        :return: tuple containing (name, description, dependencies, width)
        :rtype: tuple(str,str,list,int)
        """
        width = len(max([item['name'] for item in task_list], key=len))
        for item in sorted(task_list, key=itemgetter('name')):
            yield item['name'], item['description'], item['dependencies'], width

    def _get_default_tasks(self):
        """
        Get a list of default task names (@task(default=True)).

        :return: List containing default task names.
        :rtype: list
        """
        if 'default' in HerringTasks.keys():
            return ['default']
        return []

    def _verify_tasks_exists(self, task_list):
        """
        If a given task does not exist, then raise a ValueError exception.

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
        Builds dictionary used by toposort2 from HerringTasks

        :param src_tasks: a List of task names
        :type src_tasks: list
        :param herring_tasks: list of tasks from the herringfile
        :type herring_tasks: dict
        :return: dict where key is task name and value is List of dependency
            task names
        :rtype: dict
        """
        data = {}
        for name in src_tasks:
            data[name] = set(herring_tasks[name]['depends'])
        return data

    def _find_dependencies(self, src_tasks, herring_tasks):
        """
        Finds the dependent tasks for the given source tasks, building up an
        unordered list of tasks.

        :param src_tasks: list of task names that may have dependencies
         :type src_tasks: list
        :param herring_tasks: list of tasks from the herringfile
         :type herring_tasks: dist
        :return: list of resolved (including dependencies) task names
        :rtype: list
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
        Resolve the dependencies for the given list of task names.

        :param src_tasks: list of task names that may have dependencies
        :type src_tasks: list
        :param herring_tasks: list of tasks from the herringfile
        :type herring_tasks: dict
        :return: list of resolved (including dependencies) task names
        :rtype: list
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
        :type task_list: list
        :return: None
        """
        verified_task_list = self._verify_tasks_exists(task_list)
        for task_name in self._resolve_dependencies(verified_task_list,
                                                    HerringTasks):
            info("Running: {name} ({description})".format(name=task_name,
                                                          description=HerringTasks[task_name]['description']))
            HerringTasks[task_name]['task']()
