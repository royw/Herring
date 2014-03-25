# coding=utf-8

"""
The main Herring application.
"""
__docformat__ = 'restructuredtext en'

import os
import sys

from pathlib import Path
from operator import itemgetter
from herring.support.toposort2 import toposort2
from herring.support.simple_logger import debug, info, fatal, Logger
from herring.herring_file import HerringFile
from herring.support.utils import find_files
from herring.task_with_args import TaskWithArgs, HerringTasks, NameSpace


__all__ = ("HerringApp", "task", "run", "HerringTasks")

# Alias for task decorator just makes the herringfiles a little cleaner.
# pylint: disable=C0103
task = TaskWithArgs
run = HerringFile.run
namespace = NameSpace


# noinspection PyMethodMayBeStatic
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
        Logger.set_verbose(True)
        Logger.set_debug(False)

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

            self._load_tasks(herring_file, settings)
            task_list = list(self._get_tasks_list(HerringTasks, settings.list_all_tasks))
            if settings.list_tasks:
                cli.show_tasks(self._get_tasks(task_list), HerringTasks, settings)
            elif settings.list_task_usages:
                cli.show_task_usages(self._get_tasks(task_list), HerringTasks, settings)
            elif settings.list_dependencies:
                cli.show_depends(self._get_tasks(task_list), HerringTasks, settings)
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

    def _load_tasks(self, herringfile, settings):
        """
        Loads the given herringfile then loads any herringlib files.

        :param herringfile: the herringfile path
        :type herringfile: str
        :return: None
        """
        herringfile_path = Path(herringfile).parent
        library_paths = self._locate_library(herringfile_path, settings)
        info("library_paths: %s" % repr(library_paths))
        if library_paths:
            sys.path = [str(path.parent) for path in library_paths if path.parent != herringfile_path] + \
                       [str(herringfile_path)] + sys.path
        else:
            sys.path = [str(herringfile_path)] + sys.path
        info("sys.path: %s" % repr(sys.path))
        self._load_file(herringfile)
        for file_name in self.library_files(library_paths=library_paths):
            info("file_name = {file}".format(file=file_name))
            mod_name = 'herringlib.' + Path(file_name).stem
            info("mod_name = {name}".format(name=mod_name))
            __import__(mod_name)

    def _locate_library(self, herringfile_path, settings):
        """
        locate and validate the paths to the herringlib directories

        :param settings: the application settings
        :param herringfile_path: the herringfile path
        :type herringfile_path: str
        :return: library path
        :rtype: list(Path)
        """
        paths = []
        for lib_path in [Path(os.path.expanduser(lib_dir)) for lib_dir in settings.herringlib]:
            if not lib_path.is_absolute():
                lib_path = Path(herringfile_path, str(lib_path))
            if lib_path.is_dir():
                paths.append(lib_path)
        return paths

    @staticmethod
    def library_files(library_paths=None, pattern='*.py'):
        """
        Yield any .py files located in herringlib subdirectory in the
        same directory as the given herringfile.  Ignore package __init__.py
        files, .svn and templates sub-directories.

        :param library_paths: the path to the herringlib directory
        :type library_paths: list(Path)
        :param pattern: the file pattern (glob) to select
        :type pattern: str
        :return: iterator for path to a library herring file
        :rtype: iterator
        """
        if library_paths is None:
            return
        for lib_path in library_paths:
            info("lib_path: {path}".format(path=lib_path))
            parent_path = lib_path.parent
            if lib_path.is_dir():
                files = find_files(str(lib_path), excludes=['*/templates/*', '.svn'], includes=[pattern])
                for file_path in [Path(file_name) for file_name in files]:
                    if file_path.name == '__init__.py':
                        continue
                    debug("parent_path: %s" % str(parent_path))
                    debug("loading from herringlib:  %s" % file_path)
                    rel_path = file_path.relative_to(parent_path)
                    debug("relative path: %s" % str(rel_path))
                    yield rel_path

    def load_plugin(self, plugin, paths):
        """load a plugin module if we haven't yet loaded it
        :param plugin: the herringlib plugin to load
        :param paths: the herringlib path
        """
        # check if we haven't loaded it already
        try:
            return sys.modules[plugin]
        except KeyError:
            pass
        info("load_plugin({plugin}, {paths})".format(plugin=plugin, paths=paths))
        # ok, the load it
        #fp, filename, desc = imp.find_module(plugin, paths)
        try:
            # python3
            # noinspection PyUnresolvedReferences
            from importlib import import_module
            package = 'herringlib'
            import_module(package)
            mod = import_module(plugin, package)
        except ImportError:
            # python2
            from imp import load_module, PY_SOURCE
            filename = os.path.join(paths, plugin)
            extension = os.path.splitext(filename)[1]
            mode = 'r'
            desc = (extension, mode, PY_SOURCE)
            debug(repr(desc))
            with open(filename, mode) as fp:
                mod = load_module(plugin, fp, filename, desc)
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
            if name not in dependencies:
                dependencies.append(name)
                depend_tasks = herring_tasks[name]['depends']
                tasks = self._find_dependencies([task_ for task_ in depend_tasks if task_ not in dependencies],
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
