# coding=utf-8

"""
Provides support for the @task decorator.
"""

__all__ = ('TaskWithArgs', 'HerringTasks')


# HerringTasks dictionary
# key is task name as string
# value is dictionary with keys in ['task', 'depends']
# where value['task'] is the task function reference
# and value['depends'] is a list of string task names
# that are this task's dependencies.
HerringTasks = {}


class TaskWithArgs(object):
    """
    task decorator

    This gathers info about the task and stores it into the
    HerringApp.HerringTasks dictionary.  The decorator does not run the
    task.  The task will be invoked via the HerringApp.HerringTasks
    dictionary.

    """

    # the unused command line arguments are placed here as a list so
    # that tasks can access them as: task.argv
    argv = None
    kwargs = None

    # noinspection PyRedeclaration
    def __init__(self, *deco_args, **deco_kwargs):
        """
        keyword arguments:
            depends:  a list of task names where the task names are strings
        """
        self.deco_args = deco_args
        self.deco_kwargs = deco_kwargs
        self._settings = None

    def __call__(self, func):
        """
        invoked once when the module is loaded so we hook in here
        to build our internal task dictionary.

        :param func: the function being decorated
        :returns: function that simply invokes the decorated function
        """
        depends = []
        if 'depends' in self.deco_kwargs:
            depends = self.deco_kwargs['depends']

        def _wrap(*args, **kwargs):
            """
            A simple wrapper

            :param args: positional arguments passed through
            :param kwargs: keyword arguments passed through
            """
            return func(*args, **kwargs)

        HerringTasks[func.__name__] = {
            'task': _wrap,
            'depends': depends,
            'description': func.__doc__
        }
        return _wrap


