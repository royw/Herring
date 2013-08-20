#!/usr/bin/env python
# coding=utf-8

"""
=======
Herring
=======

Herring is a simple python make utility.  You write tasks in python, and
optionally assign dependent tasks.  The command line interface lets you easily
list the tasks and run them.

"First you must find... another shrubbery! (dramatic chord) Then, when you have
found the shrubbery, you must place it here, beside this shrubbery, only
slightly higher so you get a two layer effect with a little path running down
the middle. ("A path! A path!") Then, you must cut down the mightiest tree in
the forrest... with... a herring!"

Usage
=====

Tasks are defined by using a @task decorator on a function definition in the
project's herringfile:

    @task()
    def foo():
        \"\"\" Do something fooey \"\"\"
        #...

Task decorators can take optional keywords:

    :depends: List of task names as strings.

Example:

    @task(depends=['foo'])
    def bar():
        \"\"\" The bar for foo \"\"\"

Running a Task
--------------

To run a task, simply be in the directory with your herringfile or one of it's
sub-directories and type:

    herring foo

This will run the foo task.

    herring bar

Will run the foo task then the bar task.

Command Line Arguments
----------------------

To pass arguments to the task, simply place them on the command line as keyword
arguments.  The tasks may access the lists by using:  task.argv
Or already parsed as keyword args by using:  task.kwargs

Example:

    @task()
    def argDemo():
        print "argv: %s" % repr(task.argv)
        print "kwargs: %s" % repr(task.kwargs)

    herring argDemo --delta=3 --flag

outputs:

    argv: ['--delta=3', '--flag']
    kwargs: ['delta': 3, 'flag': True]

Available Tasks
---------------

To see the list of available tasks, run:

    herring -T
    Show tasks
    ============================================================
    herring foo        # Do something fooey
    herring bar        # The bar for foo

If you do not include a docstring for a task, the task is hidden and will not
show up in the list, although it can still be ran.

Reusing Tasks
-------------
If you have a "herringlib" directory in the same directory as your herringfile,
herring will attempt to load all .py files in it (glob: "herringlib/**/*.py").
These .py files may include tasks just like the herringfile.

You will probably want to include __init__.py in herringlib and it's sub-
directories so you can easily import the modules in your herringfile.

Recommended practice is to only place project independent tasks that can
be readily reused in your herringlib.  Project dependent tasks and methods
should still go in your herringfile.

Command line help is available
==============================

    herring --help
    usage: Herring [-h] [-f FILESPEC] [-T] [-U] [-D] [-a] [-q] [-v] [-l]
                   [tasks [tasks ...]]

    "Then, you must cut down the mightiest tree in the forrest... with... a herring!"

    Herring is a simple python make utility.  You write tasks in python, and
    optionally assign dependent tasks.  The command line interface lets you
    easily list the tasks and run them.  See --longhelp for details.

    positional arguments:
      tasks                 The tasks to run. If none specified, tries to run the
                            'default' task.

    optional arguments:
      -h, --help            show this help message and exit
      -f FILESPEC, --herringfile FILESPEC
                            The herringfile to use, by default uses "herringfile".
      -T, --tasks           Lists the tasks (with docstrings) in the herringfile.
      -U, --usage           Shows the full docstring for the tasks (with
                            docstrings) in the herringfile.
      -D, --depends         Lists the tasks (with docstrings) with their
                            dependencies in the herringfile.
      -a, --all             Lists all tasks, even those without docstrings.
      -q, --quiet           Suppress herring output.
      -v, --version         Show herring's version.
      -l, --longhelp        Long help about Herring

"""

__docformat__ = "restructuredtext en"

import fnmatch
from operator import itemgetter
import shutil
import subprocess
import textwrap

import re
import os
import sys
import argparse
import pkg_resources

from collections import deque
from herring.support.toposort2 import toposort2
from herring.support.SimpleLogger import debug, info, error, fatal, setVerbose, setDebug


__all__ = ("HerringApp", "HerringFile", "task", "ArgumentHelper", "run")

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

ROW_FORMAT = "{0:<{width1}s}  # {1:<{width2}s}"


class ArgumentHelper(object):
    """ Helper for handling command line arguments. """
    @staticmethod
    def argv_to_dict(argv):
        """
        Given a list of keyword arguments, parse into a kwargs dictionary.

        Each argument should either start with '--' indicating a key, or not,
        indicating a value.
        Also supports "--key=value" syntax.
        True will be used for the value of a key that does not have a given
        value. Multiple values will be joined with a space.

        This method does not attempt to cast any values, they all remain
        strings.

        >>> argv = ['--flag', 'false', '--foo', 'alpha', 'beta', '--bar=delta',
                '--charlie']
        >>> kwargs = ArgumentHelper.argv_to_dict(argv)
        >>> kwargs
        {'charlie': True, 'flag': 'false', 'foo': 'alpha beta', 'bar': 'delta'}
        """
        kwargs = {}
        current_key = None
        args = deque(argv)
        while args:
            arg = args.popleft()
            if arg == '--':
                ArgumentHelper.set_kwargs_flag(kwargs, current_key)
            elif arg.startswith('--'):
                ArgumentHelper.set_kwargs_flag(kwargs, current_key)
                current_key = arg[2:]
                if '=' in current_key:
                    current_key, value = current_key.split("=", 1)
                    kwargs[current_key] = value
            else:
                ArgumentHelper.merge_kwargs(kwargs, current_key, arg)
        ArgumentHelper.set_kwargs_flag(kwargs, current_key)
        return kwargs

    @staticmethod
    def set_kwargs_flag(kwargs, key):
        """ set the flag in kwargs if it has not yet been set. """
        if key is not None:
            if key not in kwargs:
                kwargs[key] = True

    @staticmethod
    def merge_kwargs(kwargs, key, value):
        """
        set the kwargs key/value pair, joining any pre-existing value with
        a space.
        """
        if key is not None:
            if key in kwargs:
                value = ' '.join([kwargs[key], value])
            kwargs[key] = value


class HerringFile(object):
    directory = ''

    @classmethod
    def run(cls, cmd_args, env=None, verbose=True):
        """ Down and dirty shell runner.  Yeah, I know, not pretty. """
        info("cmd_args => %s" % repr(cmd_args))
        info("env => %s" % repr(env))
        info("verbose => %s" % repr(verbose))
        if verbose:
            info(' '.join(cmd_args))
        lines = []
        for line in cls.runProcess(cmd_args, env=env):
            if verbose:
                sys.stdout.write(line)
            lines.append(line)
        return "".join(lines)

    @classmethod
    def runProcess(cls, exe, env=None):
        info("runProcess(%s, %s)" % (exe, env))
        sub_env = os.environ.copy()
        if env:
            for key, value in env.iteritems():
                sub_env[key] = value

        p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             env=sub_env)
        while True:
            ret_code = p.poll()   # returns None while subprocess is running
            line = p.stdout.readline()
            yield line
            if ret_code is not None:
                break


class NewProject(object):
    def __init__(self, target_dir):
        """
        Create project infrastructure for a new project.

        :param target_dir: The top level directory for the new project
        :type target_dir: str
        """
        self.full_path = os.path.abspath(target_dir)

    def populate(self):
        """
        Populate the new project.

        If there is not a herringfile in the target directory, then create one and make
        best guesses to necessary values.

        If there is not a herringlib in the target directory, then create one and populate
        with standard development tasks.

        If there is not a package directory, then create one and populate with an package_app.py
        empty file.
        """
        self._makedirs(self.full_path)
        self.initializeHerringfile(self.full_path)
        self.initializeHerringlib(self.full_path)
        self.initializePackage(self.full_path)

    def initializeHerringfile(self, dest_path):
        """
        Create an initial herringfile for the new project.

        :param dest_path: The directory where the herringfile goes
        :type dest_path: str
        """
        herring_file = os.path.join(dest_path, 'herringfile')
        if os.path.exists(herring_file):
            info("%s already exists!  Left unchanged." % herring_file)
            return
        name = os.path.basename(dest_path)
        package = name.lower()
        author = os.environ['USER']
        with open(herring_file, 'w') as outFile:
            template = pkg_resources.resource_string('herring.init', 'herringfile.template')
            try:
                outFile.write(template.format(name=name,
                                              package=package,
                                              author=author))
            except Exception as ex:
                error(ex)

    def initializeHerringlib(self, dest_path):
        """
        Create an initial populated herringlib directory.

        :param dest_path:  The parent directory for the new herringlib directory.
        :type dest_path: str
        """
        herringlib_dir = os.path.join(dest_path, 'herringlib')
        if os.path.exists(herringlib_dir):
            info("%s already exists!  Left unchanged." % herringlib_dir)
            return
        lib_dir = pkg_resources.resource_filename('herring.init', 'herringlib')
        info("copytree(%s, %s)" % (lib_dir, herringlib_dir))
        shutil.copytree(lib_dir, herringlib_dir)

    def initializePackage(self, dest_path):
        """
        Create the initial package and app file.

        :param dest_path:  The parent directory for the new package directory.
        :type dest_path: str
        """
        name = os.path.basename(dest_path)
        package_name = name.lower()
        package_dir = os.path.join(dest_path, package_name)
        if os.path.exists(package_dir):
            return
        self._makedirs(package_dir)

        init_file = os.path.join(package_dir, "__init__.py")
        open(init_file, 'w').close()

        app_file = os.path.join(package_dir, "{package}_app.py".format(package=package_name))
        with open(app_file, 'w') as outFile:
            outFile.write(textwrap.dedent("""
            def main():
                \"\"\"
                This is the console entry point

                :return: None
                \"\"\"
                pass


            if __name__ == '__main__':
                main()

            """))

    def _makedirs(self, directory_name):
        """Safely make needed directories (mkdir -p)"""
        try:
            os.makedirs(directory_name)
        except OSError, err:
            if err.errno != 17:
                raise
        return directory_name


class HerringApp(object):
    """
    This is the application class.

    Usage:
        herring = Herring(outputter=sys.stdout)
        herring.cli()
        herring.execute()
    """

    # HerringTasks dictionary
    # key is task name as string
    # value is dictionary with keys in ['task', 'depends']
    # where value['task'] is the task function reference
    # and value['depends'] is a list of string task names
    # that are this task's dependencies.
    HerringTasks = {}

    def __init__(self):
        """
        The Herring application.
        """
        setVerbose(True)
        setDebug(False)
        self._version = self._load_version()

    def _load_version(self):
        """
        Load the applications version from the VERSION.txt file

        :return: the version string or 'Unknown'
        """
        path = os.path.dirname(__file__)
        try:
            with open(os.path.join(path, 'VERSION.txt')) as version_file:
                return version_file.read().strip()
        except IOError:
            pass
        return 'Unknown'

    class TaskWithArgs(object):
        """
        task decorator

        This gathers info about the task and stores it into the
        HerringApp.HerringTasks dictionary.  The decorator does not run the
        task.  The task will be invoked via the HerringApp.HerringTasks
        dictionary.

        """

        # the unused command line arguments are placed here as a list so
        # that tasks can access them as: task.argv
        argv = None
        kwargs = None

        # noinspection PyRedeclaration
        def __init__(self, *deco_args, **deco_kwargs):
            """
            keyword arguments:
                depends:  a list of task names where the task names are strings
            """
            self.deco_args = deco_args
            self.deco_kwargs = deco_kwargs
            self._settings = None

        def __call__(self, func):
            """
            invoked once when the module is loaded so we hook in here
            to build our internal task dictionary.

            :param func: the function being decorated
            :returns: function that simply invokes the decorated function
            """
            depends = []
            if 'depends' in self.deco_kwargs:
                depends = self.deco_kwargs['depends']

            def _wrap(*args, **kwargs):
                """
                A simple wrapper

                :param args: positional arguments passed through
                :param kwargs: keyword arguments passed through
                """
                return func(*args, **kwargs)

            HerringApp.HerringTasks[func.__name__] = {
                'task': _wrap,
                'depends': depends,
                'description': func.__doc__
            }
            return _wrap

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

        self._settings, argv = self._get_settings()

        setVerbose(not self._settings.quiet)
        setDebug(self._settings.debug)

        HerringApp.TaskWithArgs.argv = argv
        HerringApp.TaskWithArgs.kwargs = ArgumentHelper.argv_to_dict(argv)

        if self._settings.longhelp:
            info(sys.modules[__name__].__doc__)
            exit(0)

        if self._settings.version:
            info("Herring version %s" % self._version)
            exit(0)

        if self._settings.init:
            proj = NewProject(self._settings.init)
            exit(proj.populate())

    def execute(self):
        """
        Execute the tasks specified in the _settings object.

        Currently:
            * _settings.list_task asserted shows the available tasks.
            * _settings.list_dependencies asserted shows the available tasks
                and their dependencies.
            * _settings.list_all_tasks asserted modifies the listing to include
                tasks that do not have a docstring.
            * if both _settings.list_task and _settings.list_dependencies are
                deasserted, then run the tasks from _settings.tasks

        :return: None
        """
        try:
            herring_file = self._find_herring_file(self._settings.herringfile)
            HerringFile.directory = str(os.path.realpath(os.path.dirname(herring_file)))
            sys.path.insert(1, HerringFile.directory)

            # the tasks are always ran with the current working directory
            # set to the directory that contains the herringfile
            os.chdir(HerringFile.directory)

            info("Using: %s" % herring_file)

            self._load_tasks(herring_file)
            task_list = list(self._get_tasks_list(HerringApp.HerringTasks,
                                                  self._settings.list_all_tasks))
            if self._settings.list_tasks:
                self._show_tasks(task_list)
            elif self._settings.list_task_usages:
                self._show_task_usages(task_list)
            elif self._settings.list_dependencies:
                self._show_depends(task_list)
            else:
                try:
                    self._run_tasks(self._settings.tasks)
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

    def _show_task_usages(self, task_list, full=False):
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
        if 'default' in HerringApp.HerringTasks.keys():
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
            task_names = HerringApp.HerringTasks.keys()
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
                                                    HerringApp.HerringTasks):
            info("Running: %s" % task_name)
            HerringApp.HerringTasks[task_name]['task']()

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


# Alias for task decorator just makes the herringfiles a little cleaner.
task = HerringApp.TaskWithArgs
run = HerringFile.run


def main():
    """
    This is the console entry point

    :return: None
    """

    herring = HerringApp()
    herring.cli()
    herring.execute()


if __name__ == '__main__':
    main()
