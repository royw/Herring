Change Log
==========

::

    * revisited requirements
    * moved generated doc files to docs/
    * updated support files.  python3 corrections.
    * doc update.  version bump
    * support herringlib project::init task
    * removed generated requirements.txt file, use the versioned files instead
    * handle wheel builds for each supported python version
    * version bump
    * removed pathlib as not portable to py2.6
    * porting across python 2.6, 2.7, 3.3, 3.4
    * added task_execute(str|list) support method.
    * require libraries dependent on python version
    * build/deploy wheel.  Python2/3 integration issues.
    * made read-only to prevent pycharm from screwing with it
    * corrected title levels
    * herringlib search path
    * python2,3 compatibility
    * python 3
    * cleanup
    * added multiple herringlib path support
    * started adding support for wheels
    * changed from nose to pytest
    * add missing doc files
    * python3 porting
    * prep for supporting config file to specify herringlib path
    * Support multiple herringlib locations
    * python3 port
    * python3 port
    * Added run timeout
    * prep for python3
    * added namespace feature
    * documentation
    * added support for dynamic terminal width detection and json output
    * documentation formatting
    * removed python 3.2
    * bump version in prep for release
    * cleanup
    * cleanup and minor test corrections.
    * cleanup
    * cleanup
    * cleanup
    * cleanup
    * updated to latest herringlib
    * dev version bump
    * pep8
    * updated documentation
    * ignore .tox directory
    * version bump
    * removed unused imports
    * version bump
    * corrected package name
    * changed info messages to debug messages
    * task and packaging cleanup
    * added tox test runner
    * if run(), switched from blocking readline to non-blocking so prompts are immediately displayed
    * corrected accessing features directory
    * corrected reference to Project
    * added support for behave BDD
    * Got working again.
    * documentation cleanup
    * Added task help message support.
    * correction in setup.py template and requirements.txt files
    * Corrected pymetrics package name
    * Changed from shutil.copytree to distutils.dir_util.copy_tree which does not require the destination to be empty.
    * corrected path given to --update
    * moved from HerringFile
    * ComparableMixin to support comparing Version objects
    * Trying to improve exception reporting for task execution.
    * Moved findFiles to herringlib/find_files.py.  Changed from using pip to using yolk for finding installed packages to work around issue debugging with pycharm.
    * Added --update to update installed herringlib generic tasks
    * Version bump
    * Replaced with generic scheme based Version object in herringlib/version.py
    * Added required packages check.
    * Replaced version bumping with generic scheme based Version object that handles bumping.
    * reformatted
    * clean up
    * Handle packages that are not in the Help dictionary.
    * Added yolk as dependency to better support installed package discovery.
    * corrected required package detection.  documentation pass
    * version bump
    * Increase gracefulness of loading 3rd party packages
    * refacture ui from herring_app to herring_cli.  documentation pass
    * refactored. Doc pass.
    * documentation pass.  Moved version to __init__.py
    * corrected case of Herring in the requirements.txt templates
    * added --init to initialize a new project.  Replaced herringlib with a generic version of the herringlib tasks.
    * support multi-line docstring comments for tasks
    * corrected module load paths
    * moved closer to getting __DIR__ to work
    * corrected updateReadme task in herringfile
    * added .gitignore
    * initial coding
