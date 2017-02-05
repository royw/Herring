# coding=utf-8

# pylint: disable=C0301,W1401
"""
What is Herring?
================

Herring is a simple python make utility.  You write tasks in python, and
optionally assign dependent tasks.  The command line interface lets you easily
list the tasks and run them.

"First you must find... another shrubbery! (dramatic chord) Then, when you have
found the shrubbery, you must place it here, beside this shrubbery, only
slightly higher so you get a two layer effect with a little path running down
the middle. ("A path! A path!") Then, you must cut down the mightiest tree in
the forrest... with... a herring!"


Tasks
=====


Task Definition
---------------

Tasks are defined by using a @task decorator on a function definition in the
project's herringfile::

    @task()
    def foo():
        \"\"\" Do something fooey \"\"\"
        #...

Task decorators can take optional keywords:

:depends:
    List of task names as strings that this task depends upon.  All depends tasks will be ran prior to this task.
    Example a task that depends on tasks "foo" and "bar" in the same namespace would be declared as:
    depends=['foo', 'bar'].  A task that depends on a task in another namespace, say task 'bar' in
    namespace 'foo', would be declared as:  depends['foo::bar'].

:dependent_of:
    Task name as string that this task is a dependent of.  This allows you to add a dependency to a third party
    task.  For example, to run a "predoc" task before generating documentation using herringlib's "doc" task,
    you would set the "dependent_of" task decorator attribute to "doc::generate".

:help:
    Text that will be shown as notes when showing tasks (ex: running "herring -T").

:namespace:
    The namespace for the task.  Examples:  "alpha", "alpha::beta", "alpha::beta::charlie",...

:private:
    A boolean that can be used to declare a task private.  The default is for each task with a docstring to
    be public while tasks without a docstring are private.  This flag overrides this behavior making the task
    private whether or not it has a docstring.

:kwargs:
    A list of command line arguments recognized by the task.  For example kwargs=['alpha', 'beta'] means
    the task can accept "--alpha=foo --beta=bar" on the herring command line.  This is intended to allow
    GUI front-ends to build a dialog prompting for the options for the task.

:arg_prompt:
    If the task requires a command line argument and none are give, use this string to prompt the user for
    the argument.  The task can access this attribute using: task.arg_prompt

:configured:
    Indicates if herringfile must be filled in.  If configured is "no", then herringfile must be
    non-existent or empty for the task to be available.  If configured is "optional", then the task is always
    available.  If configure is "required" then the task is available if the herringfile is not empty.
    "required" is default.

This example defines task "test::bar" that is dependent on task "foo"::

    @task(namespace='test', depends=['foo'], help="doesn't do anything")
    def bar():
        \"\"\" The bar for foo \"\"\"

This example shows prompting for an argument::

    @task(arg_prompt="Enter a value:")
    def foobar():
        \"\"\" This foobar needs a value \"\"\"
        if task.arg_prompt is not None:
            value = prompt(task.arg_prompt)


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

this will run the **doc::generate_icon** task then the **doc::sphinx** task then the **doc** task.

.. note::

    Herring performs a topological sort on a tasks dependencies.  This generates a list of sets of
    tasks.  The list is executed in order.  The tasks in each set are executed in parallel
    processes.  Output (both stdout and stderr) is captured while each task is ran then upon task
    completion is writen to the output.

    The --interactive flag may be used to prevent the tasks running in parallel.  Instead the tasks
    in a set are ran in random order without buffering the output.


Command Line Arguments
----------------------

To pass arguments to the task, simply place them on the command line as keyword
arguments.  The tasks may access the lists by using::

    task.argv

Or already parsed as keyword args by using::

    task.kwargs


For Example::

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
    author: Roy Wright
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

this will give you a boilerplate herringfile and populate the project with support for package building, documentation,
a MVC commandline application.

.. note::

    Project::init will provide a CLI application boilerplate code in the Project.package directory.  On
    existing projects you probably want to delete these.

Edit your herringfile, mainly verifying or changing the dictionary values being passed to Project.metadata().

.. note::

    The first time that you run herring after a project::init, more templates are installed using the metadata
    in your herringfile.  So it is very important to edit your herringfile **immediately** after running
    project::init.

To see all settings with their current values::

    ➤ herring project::describe

Now you can create the virtual environments for your project with:

    ➤ herring project::mkvenvs

.. note::

    Herringlib supports multiple virtual environments intended for supporting multiple python versions.  The virtual
    environments will be named by concatenating the **package** with each of the **python_versions** values.  For
    example, if the herringfile's metadata contained::

        Project.metadata(
        {
            'package': 'foo',       # snakecase
            'python_versions': ('35', '34', '27'),
        }

    then the following virtual environments would be created::

        foo35
        foo34
        foo27

    The other \*_version and \*_versions metadata select which virtual environments will be used in certain circumstances.
    For example::

        'test_python_versions': ('27', '35'),

    will cause "herring test" to run the test task twice, once using the foo27 virtualenv and again using foo35.


Finally you are ready to develop your project.  The following are typical command flow::

    ➤ herring test
    ➤ herring version::bump
    ➤ git add -A
    ➤ git commit -m 'blah...'
    ➤ herring doc
    ➤ herring build
    ➤ herring deploy doc::publish

To see a list of public tasks:

    ➤ herring -T

"""

__docformat__ = 'restructuredtext en'

__version__ = '0.1.49'
