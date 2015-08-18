Design
======

The application is a non-interactive CLI utility.

                A common pattern used is for a class to have an **execute()** method.  The class is initialized,
                set up, then the **execute()** method is invoked once and the class's primary function is performed.
                The instance may then be queried for results before destruction.  I'll refer to this pattern as the
                execute pattern.

herring/argument_helper.py
--------------------------

Helper for handling command line arguments.

Classes:

* ArgumentHelper


herring/herring_app.py
----------------------

The main Herring application.

For use in your herringfile or task files the following functions are exported:

* task - the task decorator
* namespace - the namespace decorator
* task_execute - execute the named (including namespace) task(s) including dependencies

Classes:

* HerringApp


herring/herring_cli.py
----------------------

The command line interface for the herring application.

Classes:

* HerringCLI


herring/herring_file.py
-----------------------

Provides built in run support methods for herringfile tasks.

Classes:

* HerringFile


herring/herring_main.py
-----------------------

This is the console entry point (from setup.py) for the herring application.

Functions:

* hack_sys_path
* main


herring/herring_settings.py
---------------------------

HarvesterSettings adds application specific information to the generic ApplicationSettings class.

Classes:

* HerringSettings


herring/task_with_args.py
-------------------------

Provides support for the @task decorator.

Supported attributes for the @task decorator are:

* depends=[string, ...] where the string is the task names that this task depends upon.
* namespace=string where string is the namespace.  Multiple namespaces may be used (ex: "one::two::three").
* help=string where string is a message appended to the list task output.
* kwargs=[string,...] where string are argument names that the task may use.
* configured=string where string must be 'no', 'optional', or 'required'.  The default is 'required'.
* private=boolean where boolean is True or False.  If private is True, then the task is not listed in the task list.
  Setting private=True is useful if you want to keep the task's docstring.  The presence of a docstring normally
  indicates a public task.

Classes:

* NameSpace
* TaskWithArgs


