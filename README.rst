
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
        """ Do something fooey """
        #...

Task decorators can take optional keywords::

    :depends: List of task names as strings.
    :help: Text that will be shown as notes when showing tasks (ex: running "herring -T").
    :namespace: The namespace for the task.

This example defines task "test::bar" that is dependent on task "foo"::

    @task(namespace='test', depends=['foo'], help="doesn't do anything")
    def bar():
        """ The bar for foo """

Namespaces
----------

Namespaces are a grouping mechanism for tasks, not to be confused with python
namespace/packages.  The purpose is so you can easily group related tasks
without using a naming convention.

For example say you had the following three documentation tasks::

    @task(depends=['doc_generate_icon'])
    def doc_sphinx():
        pass

    @task()
    def doc_generate_icon()
        pass

    @task(depends=['doc_sphinx'])
    def doc()
        pass

Using namespaces you could have something like:

    with namespace('doc'):

        @task(depends=['doc::generate_icon'])
        def sphinx():
            pass

        @task()
        def generate_icon()
            pass

    @task(depends=['doc::sphinx'])
    def doc()
        pass

Note that you may use multiple namespaces within the same module or even have tasks from different
modules in the same namespace.

Also that namespaces do not affect directly calling a method.  So you may simply call the **generate_icon()**
method directly.  Calling the method directly does not run the task's dependencies.  To run a task with it's
dependencies, use the **task_execute()** function.  For example::

    task_execute('doc')

will run the doc::sphinx dependency then the doc() task.

You may run multiple tasks by giving task_execute a list of tasks::

    task_execute(['generate_icon', 'sphinx'])

Running a Task
--------------

To run a task, simply be in the directory with your herringfile or one of it's
sub-directories and to run the **doc** task, type::

    herring doc

this will run the **doc::generate_icon** task then the **doc::sphinx** task then the **doc** task::


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

    ➤ mkvirtualenv foobar
    New python executable in foobar/bin/python
    Installing setuptools, pip...done.

    ➤ mkproject foobar
    New python executable in foobar/bin/python
    Installing setuptools, pip...done.
    Creating /home/wrighroy/projects/foobar
    Setting project for foobar to /home/wrighroy/projects/foobar

Now install Herring::

    ➤ pip install Herring
    ...
    Successfully installed Herring...
    Cleaning up...

    ➤ touch herringfile

Optionally use the companion **herringlib** task to create a project skeleton:

    ➤ git clone https://github.com/royw/herringlib.git
    ➤ herring project::init

this will give you a boilerplate herringfile and populate the herringlib directory with reusable tasks.

Note you can install the herringlib tasks into the project as above and/or install them for all
your projects by clone them into your ~/.herring directory::

    ➤ cd ~
    ➤ mkdir .herring
    ➤ cd .herring
    ➤ git clone https://github.com/royw/herringlib.git

While in your ~/.herring directory you may want to create a ~/.herring/herring.conf file with some
defaults for your projects.  For example::

    ➤ cat ~/.herring/herring.conf
    [Herring]

    [project]
    author: wrighroy
    author_email: roy.wright@hp.com
    dist_host: tpcvm143.austin.hp.com
    pypi_path: /var/pypi/dev

The [Herring] section is for command line options to herring.  The [project] section is for the defaults
in herringlib's Project object (see the generated herringfile and this will make sense).


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


