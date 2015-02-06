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
    :help: Text that will be shown as notes when showing tasks (ex: running "herring -T").
    :namespace: The namespace for the task.
    :private: A boolean that can be used to declare a task private.

This example defines task "test::bar" that is dependent on task "foo"::

    @task(namespace='test', depends=['foo'], help="doesn't do anything")
    def bar():
        \"\"\" The bar for foo \"\"\"

Task Scopes
-----------

Normal tasks (with docstrings) are public by default while hidden tasks (without docstrings)
are private.  You can make a public task private by setting the private attribute to True.
Declaring a task private lets you keep the docstring but hide the task from normal task list.
More on task scopes later.

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

Using namespaces you could have something like::

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

If you do not include a docstring for a task, then the task is hidden (private) and will not
show up in the list, although it can still be ran.

To show all tasks, including hidden tasks::

    herring --all

Reusing Tasks
-------------

Herring supports loading files from a "herringlib" directory.  This can be a single directory
or the union of several directories.  If the later, then herring will search for directories
to include in the union in the following order:

1. any directories specified with the command line option --herringlib,
2. a "herringlib" sub-directory to the directory that contains the "herringfile" file,
3. the directory specified in the "HERRINGLIB" environment variable,
4. the "~/.herring/herringlib" directory.

The union is created with the first found directory being the top most.  This means that if the
same filename exists in multiple found directories, the version in the first found directory will
be used.

Technically herring will create a temporary directory and copy the contents from the found directories
in the order found but not overwriting files.  Herring automatically deletes this temporary directory
unless you tell it not to with the --leave_union_dir flag (sometimes useful for debugging).

The environment variable approach is good for using a common set of tasks among a group of projects.
The sub-directory approach is good for using project specific tasks.
The "~/.herring/herringlib" approach is good for having your own set of default tasks.

Herring will attempt to load all .py files in the virtual "herringlib" directory (glob: "herringlib/\*\*/\*.py").
These .py files may include tasks just like the herringfile.

You will probably want to include __init__.py in herringlib and it's sub-directories so
you can easily import the modules in your herringfile.

Recommended practice is to group related tasks and support methods in modules in
the herringlib directory.  Making these tasks project independent facilitates code
reuse.  See the *herringlib* project (https://github.com/royw/herringlib) for some
reusable herring tasks.

Quick Project Initialization using herringlib project
-----------------------------------------------------

Herring with herringlib can initialize a new project with a herringfile and a set of generic
tasks in the herringlib.  Further this set of generic tasks can populate your
project with common infrastructure files.

Install Herring into your system python::

    ➤ sudo pip install Herring

You can install the herringlib tasks into the project and/or install them for all
your projects by clone them into your ~/.herring directory::

    ➤ mkdir -p ~/.herring
    ➤ cd ~/.herring
    ➤ git clone https://github.com/royw/herringlib.git

While in your ~/.herring directory you may want to create a ~/.herring/herring.conf file with some
defaults for your projects.  For example::

    ➤ cat ~/.herring/herring.conf
    [Herring]

    [project]
    author: wrighroy
    author_email: roy.wright@example
    dist_host: pypi.example.com
    pypi_path: /var/pypi/dev

The [Herring] section is for command line options to herring.  The [project] section is for the defaults
in herringlib's Project object (see the generated herringfile and this will make sense).

Here's an example session showing the quick project initialization.

Either create a new project or start a new one.

Change to the project's directory then create a herringfile::

    ➤ touch herringfile

Create the development environment by running::

    ➤ herring project::init

this will give you a boilerplate herringfile and populate the herringlib directory with reusable tasks.

.. note::

    Project::init will provide a CLI application boilerplate code in the Project.package directory.  On
    existing projects you probably want to delete these.

Edit your herringfile, mainly verifying or changing the dictionary values being passed to Project.metadata().

To see all settings with their current values::

    ➤ herring project::describe

Now you can create the virtual environments for your project with:

    ➤ herring project::mkvenvs

Finally you are ready to develop your project.  The following are typical command flow::

    ➤ herring test
    ➤ herring version::bump
    ➤ git add -A
    ➤ git commit -m 'blah...'
    ➤ herring build
    ➤ herring doc
    ➤ herring deploy doc::publish

To see a list of public tasks:

    ➤ herring -T


Command line help is available
==============================

To display the help message::

    ➤ herring/herring_main.py --help
    usage: Herring [-h] [-c FILE] [-f FILESPEC] [--herringlib [DIRECTORY [DIRECTORY ...]]] [-T] [-U] [-D] [-a] [-q] [-d]
                   [--herring_debug] [--leave_union_dir] [-j] [-v] [-l]
                   [tasks [tasks ...]]

    "Then, you must cut down the mightiest tree in the forrest... with... a herring!" Herring is a simple python make
    utility. You write tasks in python, and optionally assign dependent tasks. The command line interface lets you easily
    list the tasks and run them. See --longhelp for details.

    optional arguments:
      -h, --help                  show this help message and exit
      -c FILE, --conf_file FILE   Configuration file in INI format (default: ['.herringrc',
                                  '/home/wrighroy/.herring/herring.conf', '/home/wrighroy/.herringrc'])

    Config Group:

      -f FILESPEC, --herringfile FILESPEC
                                  The herringfile name to use, by default uses "herringfile".
      --herringlib [DIRECTORY [DIRECTORY ...]]
                                  The location of the herringlib directory to use (default: ['herringlib',
                                  '~/.herring/herringlib']).

    Task Commands:

      -T, --tasks                 Lists the public tasks (with docstrings).
      -U, --usage                 Shows the full docstring for the tasks (with docstrings).
      -D, --depends               Lists the tasks (with docstrings) with their dependencies.
      tasks                       The tasks to run. If none specified, tries to run the 'default' task.

    Task Options:

      -a, --all                   Lists all tasks, even those without docstrings.

    Output Options:

      -q, --quiet                 Suppress herring output.
      -d, --debug                 Display task debug messages.
      --herring_debug             Display herring debug messages.
      --leave_union_dir           Leave the union herringlib directory on disk (do not automatically erase). Useful for
                                  debugging.
      -j, --json                  Output list tasks (--tasks, --usage, --depends, --all) in JSON format.

    Informational Commands:

      -v, --version               Show herring's version.
      -l, --longhelp              Long help about Herring.

"""

__docformat__ = 'restructuredtext en'

__version__ = '0.1.25'
