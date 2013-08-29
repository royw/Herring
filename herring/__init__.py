# coding=utf-8

# pylint: disable=C0301,W1401
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
project's herringfile::

    @task()
    def foo():
        \"\"\" Do something fooey \"\"\"
        #...

Task decorators can take optional keywords::

    :depends: List of task names as strings.

Example::

    @task(depends=['foo'])
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
        print "argv: %s" % repr(task.argv)
        print "kwargs: %s" % repr(task.kwargs)

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

Reusing Tasks
-------------

If you have a "herringlib" directory in the same directory as your herringfile,
herring will attempt to load all .py files in it (glob: "herringlib/\*\*/\*.py").
These .py files may include tasks just like the herringfile.

You will probably want to include __init__.py in herringlib and it's sub-
directories so you can easily import the modules in your herringfile.

Recommended practice is to only place project independent tasks that can
be readily reused in your herringlib.  Project dependent tasks and methods
should still go in your herringfile.

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

    ➤ pip install -i http://tpcvm143.austin.hp.com/pypi/simple Herring
    ...
    Successfully installed Herring
    Cleaning up...

Now create the project's root directory and populate it for Herring::

    ➤ herring --init FooBar

    ➤ cd FooBar

    ➤ ls
    foobar  herringfile  herringlib

    ➤ ls herringlib/
    cd.py      doc.pyc          metrics.py             recursively_remove.pyc  setup_tasks.py   version.py
    cd.pyc     __init__.py      metrics.pyc            runner.py               setup_tasks.pyc  version.pyc
    clean.py   __init__.pyc     project_settings.py    runner.pyc              templates
    clean.pyc  list_helper.py   project_settings.pyc   safe_edit.py            tests.py
    doc.py     list_helper.pyc  recursively_remove.py  safe_edit.pyc           tests.pyc

    ➤ ls foobar
    foobar_app.py  __init__.py

Let's see what tasks we now have::

    ➤ herring -T
    Using: ~/projects/foobar/FooBar/herringfile
    No module named ordereddict
    No module named ordereddict
    No module named ordereddict
    No module named pxssh
    Show tasks
    ================================================================================
    herring apiDoc      # Generate API sphinx source files from code
    herring bump        # Bumps the patch version in VERSION file up by one.
    herring cheesecake  # Run the cheesecake kwalitee metric
    herring clean       # remove build artifacts
    herring complexity  # Run McCabe code complexity
    herring doc         # Generate API documents
    herring docClean    # Remove documentation artifacts
    herring epyDocs     # Generate epy API documents
    herring lint        # Run pylint with project overrides from pylint.rc
    herring metrics     # Quality metrics
    herring purge       # remove unnecessary files
    herring sphinxDocs  # Generate sphinx API documents
    herring test        # Run the unit tests
    herring version     # Show the current version

Oops, looks like we need a couple of packages installed::

    ➤ pip install ordereddict pexpect
    Downloading/unpacking ordereddict
    ...
    Successfully installed ordereddict pexpect
    Cleaning up...

    ➤ herring -T
    Using: ~/projects/foobar/FooBar/herringfile
    version_file => ~/projects/foobar/FooBar/foobar/__init__.py
    version_file => ~/projects/foobar/FooBar/foobar/VERSION.txt
    version_file => ~/projects/foobar/FooBar/foobar/__init__.py
    Show tasks
    ================================================================================
    herring apiDoc             # Generate API sphinx source files from code
    herring build              # build the project as a source distribution
    herring bump               # Bumps the patch version in VERSION file up by one.
    herring checkRequirements  # Checks that herringfile and herringlib/* required
                               # packages are in requirements.txt file
    herring cheesecake         # Run the cheesecake kwalitee metric
    herring clean              # remove build artifacts
    herring complexity         # Run McCabe code complexity
    herring default            # The default task(s) to run when none are specified
    herring deploy             # copy latest sdist tar ball to server
    herring doc                # Generate API documents
    herring docClean           # Remove documentation artifacts
    herring epyDocs            # Generate epy API documents
    herring install            # install the project
    herring lint               # Run pylint with project overrides from pylint.rc
    herring metrics            # Quality metrics
    herring purge              # remove unnecessary files
    herring sphinxDocs         # Generate sphinx API documents
    herring test               # Run the unit tests
    herring uninstall          # uninstall the project
    herring updateReadme       # Update the README.txt from the application's
                               # --longhelp output
    herring version            # Show the current version

That's better.  Here's a little of the generic tasks' magic (specifically project_settings)::

    ➤ ls
    build        dist  faq.txt  FooBar.egg-info  herringlib   license.txt  news.txt   quality     report            setup.py  thanks.txt
    CHANGES.txt  docs  foobar   herringfile      install.txt  MANIFEST.in  pylint.rc  README.txt  requirements.txt  tests     todo.txt

What happened was when herring loaded the herringfile, the herringfile executed Project.requiredFiles() which rendered
the herringlib/templates to the project root.

The last step is to install all the third party packages used by the generic tasks::

    ➤ pip install -r requirements.txt
    ...
    Downloading/unpacking matplotlib (from -r requirements.txt (line 8))
      Downloading matplotlib-1.3.0.tar.gz (42.1Mb): 42.1Mb downloaded
      Running setup.py egg_info for package matplotlib
        The required version of distribute (>=0.6.28) is not available,
        and can't be installed while this script is running. Please
        install a more recent version first, using
        'easy_install -U distribute'.

        (Currently using distribute 0.6.24 (~/projects/foobar/lib/python2.7/site-packages/distribute-0.6.24-py2.7.egg))
        Complete output from command python setup.py egg_info:
        The required version of distribute (>=0.6.28) is not available,

    and can't be installed while this script is running. Please

    install a more recent version first, using

    'easy_install -U distribute'.



    (Currently using distribute 0.6.24 (~/projects/foobar/lib/python2.7/site-packages/distribute-0.6.24-py2.7.egg))

    ----------------------------------------
    Command python setup.py egg_info failed with error code 2 in ~/projects/foobar/build/matplotlib
    Storing complete log in ~/.pip/pip.log

Brain dead pip unfortunately requires a few iterations to install all the dependencies in the requirements.txt file,
so we will do what it says, then run the install -r requirements.txt again.  And again::

    ➤ pip install --upgrade distribute
    ...
    Successfully installed distribute setuptools
    Cleaning up...

    ➤ pip install -r requirements.txt
    ...
    REQUIRED DEPENDENCIES AND EXTENSIONS

    Requires numpy 1.5 or later to build.  (Numpy not found)

    ----------------------------------------
    Command python setup.py egg_info failed with error code 1 in ~/projects/foobar/build/matplotlib
    Storing complete log in ~/.pip/pip.log

    ➤ pip install numpy
    ...
    Successfully installed numpy
    Cleaning up...

    ➤ pip install -r requirements.txt
    ...
    Successfully installed Pygments Sphinx cheesecake coverage mako matplotlib nose pycabehtml pylint pymetrics
    sphinx-bootstrap-theme sphinx-pyreverse sphinxcontrib-plantuml sphinxcontrib-blockdiag sphinxcontrib-actdiag
    sphinxcontrib-nwdiag sphinxcontrib-seqdiag Jinja2 docutils MarkupSafe python-dateutil tornado pyparsing
    logilab-common astroid blockdiag actdiag nwdiag seqdiag six funcparserlib webcolors PIL
    Cleaning up...

Whoop!  Everything is finally installed!  Now all the tasks should work.  So start coding your foobar_app!


Command line help is available
==============================

To display the help message::

    herring --help
    usage: Herring [-h] [-f FILESPEC] [-T] [-U] [-D] [-a] [-q] [-d] [-v] [-l]
                   [-i DIRSPEC]
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
      -i DIRSPEC, --init DIRSPEC
                            Initialize a new project to use Herring. Creates
                            herringfile and herringlib in the given directory.

"""

__docformat__ = 'restructuredtext en'

__version__ = '0.0.38'
