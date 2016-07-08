# coding=utf-8

"""
The main Herring application.

For use in your herringfile or task files the following functions are exported:

* task - the task decorator
* namespace - the namespace decorator
* task_execute - execute the named (including namespace) task(s) including dependencies

The HerringApp will:

* search for and copy herringlib directories to a temp directory forming a union of contents.
* search for and load the herringfile (starts search in current directory then proceeds up the directory chain
* loads all of the modules in the temp directory.  Note that task decorator will populate the HerringTasks
  dictionary on module import.
* runs the given tasks and their dependencies.  By default, dependencies are ran in parallel processes.


"""

import os
import sys

from operator import itemgetter

from herring.herring_loader import HerringLoader
from herring.herring_runner import HerringRunner
from herring.support.simple_logger import info, fatal
from herring.herring_file import HerringFile
# from herring.support.unionfs import unionfs, unionfs_available
from herring.support.touch import touch
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

            herringfile_is_nonempty = self._is_herring_file_nonempty(herring_file)

            global debug_mode
            global verbose_mode
            debug_mode = settings.debug
            verbose_mode = not settings.quiet

            # the tasks are always ran with the current working directory
            # set to the directory that contains the herringfile
            os.chdir(HerringFile.directory)

            if not settings.json:
                info("Using: %s" % herring_file)

            if not settings.json and settings.environment:
                cli.show_environment()

            with HerringLoader(settings) as loader:
                loader.load_tasks(herring_file)  # populates HerringTasks

                task_list = list(self._get_tasks_list(HerringTasks,
                                                      settings.list_all_tasks,
                                                      herringfile_is_nonempty,
                                                      settings.tasks))

                if settings.list_tasks:
                    cli.show_tasks(self._get_tasks(task_list), HerringTasks, settings)
                elif settings.list_task_usages:
                    cli.show_task_usages(self._get_tasks(task_list), HerringTasks, settings)
                elif settings.list_dependencies:
                    cli.show_depends(self._get_tasks(task_list), HerringTasks, settings)
                else:
                    try:
                        HerringRunner.run_tasks(settings.tasks)
                    except Exception as ex:
                        fatal(ex)
        except ValueError as ex:
            fatal(ex)

    def _is_herring_file_nonempty(self, herringfile):
        return os.stat(herringfile).st_size != 0

    def _find_herring_file(self, herringfile):
        """
        Tries to locate the herringfile in the current directory, if not found
        then tries the parent directory, repeat until either found or the root
        is hit.  If not found, then create a herringfile in the current directory.

        :param herringfile: the base file name for the herringfile
        :type herringfile: str
        :return: the filespec to the found herringfile
        :rtype: str
        """
        cwd = os.getcwd()
        while cwd:
            try:
                file_spec = os.path.join(cwd, herringfile)
                with open(file_spec):
                    pass
                return file_spec
            except IOError:
                # not in current directory so go up a directory and look again
                cwd = os.sep.join(cwd.split(os.sep)[0:-1])

        # not found, so create in current directory
        file_spec = os.path.join(os.getcwd(), herringfile)
        touch(file_spec)
        return file_spec

    def _get_tasks_list(self, herring_tasks, all_tasks_flag, configured_herringfile, parameters):
        """
        A generator to massage the tasks structure into an easier to access dict.

        :param herring_tasks: the herring task structure
        :type herring_tasks: dict
        :param all_tasks_flag: asserted to include all tasks, deasserted to
            only include tasks with a docstring
        :type all_tasks_flag: bool
        :yields: a task_list dictionary {name: '...', description: '...',
            dependencies: ['...']
        :ytype: dict
        """

        for task_name in herring_tasks.keys():
            description = herring_tasks[task_name]['description']
            private = herring_tasks[task_name]['private']
            configured = herring_tasks[task_name]['configured']
            if all_tasks_flag or (not private and description is not None):
                if ((configured == 'required' and configured_herringfile) or
                        (configured == 'no' and not configured_herringfile) or
                        (configured == 'optional')):
                    # if we are doing a show (-T, -D, -U) and we give another parameter, then only show
                    # tasks that contain the parameter.  Example:  "-T doc" will show only the "doc" tasks.
                    # FYI parameters, which comes from settings.tasks, is a list of the extra parameters.
                    # So if parameters is None or empty, we want to yield all available tasks,
                    # otherwise only yield tasks that contain a parameter in the task_name.
                    if (parameters is None) or (not parameters) or [t for t in parameters if t in task_name]:
                        yield ({'name': task_name,
                                'description': str(description),
                                'dependencies': herring_tasks[task_name]['depends'],
                                'dependent_of': herring_tasks[task_name]['dependent_of'],
                                'kwargs': herring_tasks[task_name]['kwargs'],
                                'arg_prompt': herring_tasks[task_name]['arg_prompt']})

    def _get_tasks(self, task_list):
        """
        Generator for getting the sorted list of tasks with descriptions and dependencies
        for show tasks features.

        :param task_list: list of task names to show.
        :type task_list: list
        :yields: tuple containing (name, description, dependencies, width)
        :ytype: tuple(str,str,list,int)
        """
        width = len(max([item['name'] for item in task_list], key=len))
        for item in sorted(task_list, key=itemgetter('name')):
            yield(item['name'],
                  item['description'],
                  item['dependencies'],
                  item['dependent_of'],
                  item['kwargs'],
                  item['arg_prompt'],
                  width)


task_execute = HerringRunner.run_tasks
