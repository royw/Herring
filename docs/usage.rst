

Usage
=====

::

    ➤ herring.herring_main --help
    usage: Herring [-h] [-c FILE] [-f FILESPEC] [--herringlib [DIRECTORY [DIRECTORY ...]]] [-T] [-U] [-D] [-a] [-q] [-d]
                   [--herring_debug] [-j] [-v] [-l]
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
    
      -T, --tasks                 Lists the tasks (with docstrings) in the herringfile.
      -U, --usage                 Shows the full docstring for the tasks (with docstrings) in the herringfile.
      -D, --depends               Lists the tasks (with docstrings) with their dependencies in the herringfile.
      tasks                       The tasks to run. If none specified, tries to run the 'default' task.
    
    Task Options:
    
      -a, --all                   Lists all tasks, even those without docstrings.
    
    Output Options:
    
      -q, --quiet                 Suppress herring output.
      -d, --debug                 Display task debug messages.
      --herring_debug             Display herring debug messages.
      -j, --json                  Output list tasks (--tasks, --usage, --depends, --all) in JSON format.
    
    Informational Commands:
    
      -v, --version               Show herring's version.
      -l, --longhelp              Long help about Herring.
    
