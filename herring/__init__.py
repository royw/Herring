# coding=utf-8

# pylint: disable=C0301,W1401
"""
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
-----

Tasks are defined by using a @task decorator on a function definition in the
project's herringfile::

    @task()
    def foo():
        \"\"\" Do something fooey \"\"\"
        #...

Task decorators can take optional keywords::

    :depends: List of task names as strings.
    :help: Text that will be shown as notes when showing tasks.

Example::

    @task(depends=['foo'], help="doesn't do anything")
    def bar():
        \"\"\" The bar for foo \"\"\"

Running a Task
--------------

To run a task, simply be in the directory with your herringfile or one of it's
sub-directories and to run the foo task, type::

    herring foo

And this will run the foo task then the bar task::

    herring bar


Command Line Arguments
----------------------

To pass arguments to the task, simply place them on the command line as keyword
arguments.  The tasks may access the lists by using::

    task.argv

Or already parsed as keyword args by using::

    task.kwargs

Example::

    @task()
    def argDemo():
        print("argv: %s" % repr(task.argv))
        print("kwargs: %s" % repr(task.kwargs))

    herring argDemo --delta=3 --flag

outputs::

    argv: ['--delta=3', '--flag']
    kwargs: ['delta': 3, 'flag': True]

Available Tasks
---------------

To see the list of available tasks, run::

    herring -T
    Show tasks
    ============================================================
    herring foo        # Do something fooey
    herring bar        # The bar for foo

If you do not include a docstring for a task, the task is hidden and will not
show up in the list, although it can still be ran.

To show all tasks, including hidden tasks::

    herring --all

Reusing Tasks
-------------

Herring supports loading files from a "herringlib" directory.  The search order
for finding the "herringlib" to use is:

1. the directory specified in the "HERRINGLIB" environment variable,
2. a "herringlib" sub-directory to the directory that contains the "herringfile" file,
3. the "~/.herring/herringlib" directory.

The environment variable approach is good for using a common set of tasks among a group of projects.
The sub-directory approach is good for using project specific tasks.
The "~/.herring/herringlib" approach is good for having your own set of default tasks.

Herring will attempt to load all .py files in the "herringlib" directory (glob: "herringlib/\*\*/\*.py").
These .py files may include tasks just like the herringfile.

You will probably want to include __init__.py in herringlib and it's sub-
directories so you can easily import the modules in your herringfile.

Recommended practice is to group related tasks and support methods in modules in
the herringlib directory.  Making these tasks project independent facilitates code
reuse.  See the herringlib project for some reusable herring tasks.

Quick Project Initialization
----------------------------

Herring can initialize a new project with a herringfile and a set of generic
tasks in the herringlib.  Further this set of generic tasks can populate your
project with common infrastructure files.

Here's an example session showing the quick project initialization.

Start with a new virtual environment::

    ➤ virtualenv --no-site-packages foobar
    The --no-site-packages flag is deprecated; it is now the default behavior.
    New python executable in foobar/bin/python
    Installing distribute.............................................................................................
    ................................................................................................done.
    Installing pip...............done.

    ➤ cd foobar

    ➤ . bin/activate

Now install Herring::

    ➤ pip install Herring
    ...
    Successfully installed Herring
    Cleaning up...

Finally create your project sub-directory and create a herringfile in it:

    ➤ mkdir FooBar
    ➤ cd FooBar
    ➤ touch herringfile

Optionally use the companion **herringlib** utility:

    ➤ herringlib --install FooBar
    ➤ cd FooBar

this will give you a boilerplate herringfile and populate the herringlib directory with reusable tasks.


Command line help is available
==============================

To display the help message::

    ➤ herring --help
    usage: Herring [-h] [-f FILESPEC] [-T] [-U] [-D] [-a] [-q] [-d] [-v] [-l]
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
      -d, --debug           Display debug messages
      -v, --version         Show herring's version.
      -l, --longhelp        Long help about Herring

"""

__docformat__ = 'restructuredtext en'

__version__ = '0.1.6'
