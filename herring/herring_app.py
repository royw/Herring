# coding=utf-8

"""
The main Herring application.

For use in your herringfile or task files the following functions are exported:

* task - the task decorator
* namespace - the namespace decorator
* task_execute - execute the named (including namespace) task(s) including dependencies
"""

import os
from pprint import pformat
import sys

from operator import itemgetter
import tempfile
import shutil

from herring.support.list_helper import is_sequence, unique_list
from herring.support.mkdir_p import mkdir_p
from herring.support.path import Path
from herring.support.toposort2 import toposort2
from herring.support.simple_logger import debug, info, fatal
from herring.herring_file import HerringFile
# from herring.support.unionfs import unionfs, unionfs_available
from herring.support.utils import find_files
from herring.task_with_args import TaskWithArgs, HerringTasks, NameSpace

__docformat__ = 'restructuredtext en'
__all__ = ("HerringApp", "task", "HerringTasks", "task_execute", "debug_mode", "verbose_mode")

# Alias for task decorator just makes the herringfiles a little cleaner.
# pylint: disable=C0103
task = TaskWithArgs
namespace = NameSpace
debug_mode = False
verbose_mode = True


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
        global debug_mode
        global verbose_mode
        self.__sys_path = sys.path[:]
        self.union_dir = None

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
            HerringFile.settings = settings
            herring_file = self._find_herring_file(settings.herringfile)
            HerringFile.directory = str(os.path.realpath(os.path.dirname(herring_file)))
            sys.path.insert(1, HerringFile.directory)

            global debug_mode
            global verbose_mode
            debug_mode = settings.debug
            verbose_mode = not settings.quiet

            # the tasks are always ran with the current working directory
            # set to the directory that contains the herringfile
            os.chdir(HerringFile.directory)

            info("Using: %s" % herring_file)

            if settings.environment:
                cli.show_environment()

            self._load_tasks(herring_file, settings)
            task_list = list(self._get_tasks_list(HerringTasks, settings.list_all_tasks))

            # if we are doing a show (-T, -D, -U) and we give another parameter, then only show
            # tasks that contain the parameter.  Example:  "-T doc" will show only the "doc" tasks.
            if settings.tasks:
                abridged_task_list = []
                for task_ in settings.tasks:
                    abridged_task_list.extend(list([t for t in task_list if task_ in t['name']]))
                task_list = abridged_task_list

            if settings.list_tasks:
                cli.show_tasks(self._get_tasks(task_list), HerringTasks, settings)
            elif settings.list_task_usages:
                cli.show_task_usages(self._get_tasks(task_list), HerringTasks, settings)
            elif settings.list_dependencies:
                cli.show_depends(self._get_tasks(task_list), HerringTasks, settings)
            else:
                try:
                    HerringApp.run_tasks(settings.tasks)
                except Exception as ex:
                    fatal(ex)
        except ValueError as ex:
            fatal(ex)
        finally:
            if self.union_dir is not None and not settings.leave_union_dir:
                # noinspection PyTypeChecker
                shutil.rmtree(os.path.dirname(self.union_dir))

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

        self.union_dir = mkdir_p(os.path.join(tempfile.mkdtemp(), 'herringlib'))
        for src_dir in [os.path.abspath(str(path)) for path in reversed(library_paths)]:
            info("src_dir: %s" % src_dir)
            for src_root, dirs, files in os.walk(src_dir):
                files = [f for f in files if not (f[0] == '.' or f.endswith('.pyc'))]
                dirs[:] = [d for d in dirs if not (d[0] == '.' or d == '__pycache__')]
                rel_root = os.path.relpath(src_root, start=src_dir)
                dest_root = os.path.join(self.union_dir, rel_root)
                mkdir_p(dest_root)
                for basename in [name for name in files]:
                    src_name = os.path.join(src_root, basename)
                    dest_name = os.path.join(dest_root, basename)
                    try:
                        shutil.copy(src_name, dest_name)
                    except shutil.Error:
                        pass

        self._load_modules(herringfile, [Path(self.union_dir)])

    def _load_modules(self, herringfile, library_paths):
        """

        :param herringfile:
        :type herringfile:
        :param library_paths:
        :type library_paths: list[Path]
        :return:
        :rtype:
        """
        herringfile_path = Path(herringfile).parent
        debug("library_paths: %s" % repr(library_paths))
        HerringFile.herringlib_paths = [str(path.parent) for path in library_paths
                                        if path.parent != herringfile_path] + [str(herringfile_path)]
        sys.path = unique_list(HerringFile.herringlib_paths + self.__sys_path[:])

        for path in HerringFile.herringlib_paths:
            debug("herringlib path: %s" % path)
        debug(pformat("sys.path: %s" % repr(sys.path)))

        try:
            self._load_file(herringfile)
        except ImportError as ex:
            debug(str(ex))
            debug('failed to import herringfile')

        try:
            __import__('herringlib')
            debug('imported herringlib')
        except ImportError as ex:
            debug(str(ex))
            debug('failed to import herringlib')

        for lib_path in library_paths:
            sys.path = [lib_path] + self.__sys_path
            debug("sys.path: %s" % repr(sys.path))
            for file_name in self.library_files(library_paths=[lib_path]):
                mod_name = 'herringlib.' + Path(file_name).stem
                try:
                    __import__(mod_name)
                    debug('imported {name}'.format(name=mod_name))
                except ImportError as ex:
                    debug(str(ex))
                    debug('failed to import {name}'.format(name=mod_name))

        sys.path = self.__sys_path[:]

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
        :rtype: iterator[str]
        """
        if library_paths is None:
            return
        for lib_path in library_paths:
            debug("lib_path: {path}".format(path=lib_path))
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

    def _load_plugin(self, plugin, paths):
        """load a plugin module if we haven't yet loaded it
        :param plugin: the herringlib plugin to load
        :param paths: the herringlib path
        """
        # check if we haven't loaded it already
        try:
            return sys.modules[plugin]
        except KeyError:
            pass
        # ok not found so load it
        debug("_load_plugin({plugin}, {paths})".format(plugin=plugin, paths=paths))

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
        self._load_plugin(plugin, path)

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
            private = herring_tasks[task_name]['private']
            if all_tasks_flag or (not private and description is not None):
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

    @staticmethod
    def _get_default_tasks():
        """
        Get a list of default task names (@task(default=True)).

        :return: List containing default task names.
        :rtype: list
        """
        if 'default' in HerringTasks.keys():
            return ['default']
        return []

    @staticmethod
    def _verified_tasks(task_list):
        """
        If a given task does not exist, then raise a ValueError exception.

        :return: None
        :raises ValueError:
        """
        if not task_list:
            task_list = HerringApp._get_default_tasks()
        if not task_list:
            raise ValueError("No tasks given")
        task_names = HerringTasks.keys()
        return [name for name in task_list if name in task_names]

    @staticmethod
    def _tasks_to_depend_dict(src_tasks, herring_tasks):
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

    @staticmethod
    def _find_dependencies(src_tasks, herring_tasks):
        """
        Finds the dependent tasks for the given source tasks, building up an
        unordered list of tasks.

        :param src_tasks: list of task names that may have dependencies
         :type src_tasks: list
        :param herring_tasks: list of tasks from the herringfile
         :type herring_tasks: dict
        :return: list of resolved (including dependencies) task names
        :rtype: list
        """
        dependencies = []
        for name in src_tasks:
            if name not in dependencies:
                dependencies.append(name)
                depend_tasks = herring_tasks[name]['depends']
                tasks = HerringApp._find_dependencies([task_ for task_ in depend_tasks if task_ not in dependencies],
                                                      herring_tasks)
                dependencies.extend(tasks)
        return dependencies

    @staticmethod
    def _resolve_dependencies(src_tasks, herring_tasks):
        """
        Resolve the dependencies for the given list of task names.

        :param src_tasks: list of task names that may have dependencies
        :type src_tasks: list
        :param herring_tasks: list of tasks from the herringfile
        :type herring_tasks: dict
        :return: list of resolved (including dependencies) task names
        :rtype: list
        """
        tasks = HerringApp._find_dependencies(src_tasks, herring_tasks)
        task_list = []
        depend_dict = HerringApp._tasks_to_depend_dict(tasks, herring_tasks)
        for task_group in toposort2(depend_dict):
            task_list.extend(list(task_group))
        return task_list

    @staticmethod
    def run_tasks(task_list):
        """
        Runs the tasks given on the command line.

        :param task_list: a task name or a list of task names to run
        :type task_list: str|list
        :return: None
        """
        if not is_sequence(task_list):
            task_list = [task_list]

        verified_task_list = HerringApp._verified_tasks(task_list)
        info("task_list: {tasks}".format(tasks=task_list))
        info("verified_task_list: {tasks}".format(tasks=verified_task_list))
        if not verified_task_list:
            raise ValueError('No tasks given.  Run "herring -T" to see available tasks.')
        TaskWithArgs.argv = list([arg for arg in task_list if arg not in verified_task_list])
        for task_name in HerringApp._resolve_dependencies(verified_task_list, HerringTasks):
            info("Running: {name} ({description})".format(name=task_name,
                                                          description=HerringTasks[task_name]['description']))
            HerringTasks[task_name]['task']()


task_execute = HerringApp.run_tasks
