Design
======

The application is a non-interactive CLI utility.

                A common pattern used is for a class to have an **execute()** method.  The class is initialized,
                set up, then the **execute()** method is invoked once and the class's primary function is performed.
                The instance may then be queried for results before destruction.  I'll refer to this pattern as the
                execute pattern.

argument_helper.py
------------------

Helper for handling command line arguments.

herring_cli.py
--------------

The command line interface for the herring application.

herring_app.py
--------------

The main Herring application.

For use in your herringfile or task files the following functions are exported:

* task - the task decorator
* namespace - the namespace decorator
* task_execute - execute the named (including namespace) task(s) including dependencies

task_with_args.py
-----------------

Provides support for the @task decorator.

herring_settings.py
-------------------

HarvesterSettings adds application specific information to the generic ApplicationSettings class.

herring_file.py
---------------

Provides built in run support methods for herringfile tasks.

herring_main.py
---------------

This is the console entry point (from setup.py) for the herring application.

