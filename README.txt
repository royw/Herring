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
        """ Do something fooey """
        #...

Task decorators can take optional keywords:

    :depends: List of task names as strings.

Example:

    @task(depends=['foo'])
    def bar():
        """ The bar for foo """

To run a task, simply be in the directory with your herringfile or one of it's
sub-directories and type:

    herring foo

This will run the foo task.

    herring bar

Will run the foo task then the bar task.

To pass arguments to the task, simply place them on the command line as keyword
arguments.  The tasks may access the lists by using:  task.argv
Example:

    @task()
    def foo():
        print "arguments: %s" % repr(task.argv)

    herring foo --delta=3 --flag

outputs:

    arguments: ['--delta=3', '--flag']

To see the list of available tasks, run:

    herring -T
    Show tasks
    ============================================================
    herring foo        # Do something fooey
    herring bar        # The bar for foo

If you do not include a docstring for a task, the task is hidden and will not
show up in the list, although it can still be ran.

Command line help is available
==============================

    herring --help
    usage: Herring [-h] [-f FILESPEC] [-T] [-D] [-a] [-q] [-v] [tasks [tasks ...]]

    "Then, you must cut down the mightiest tree in the forrest... with... a
    herring!"

    positional arguments:
      tasks                 The tasks to run. If none specified, tries to run the
                            'default' task.

    optional arguments:
      -h, --help            show this help message and exit
      -f FILESPEC, --herringfile FILESPEC
                            The herringfile to use, by default uses "herringfile".
      -T, --tasks           Lists the tasks (with docstrings) in the herringfile.
      -D, --depends         Lists the tasks (with docstrings) with their
                            dependencies in the herringfile.
      -a, --all             Lists all tasks, even those without docstrings.
      -q, --quiet           Suppress herring output.
      -v, --version         Show herring's version.
