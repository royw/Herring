# coding=utf-8

"""
Provides support for the @task decorator.
"""
import traceback
import sys

__docformat__ = 'restructuredtext en'

from herring.support.simple_logger import fatal

__all__ = ('TaskWithArgs', 'HerringTasks')


# HerringTasks dictionary
# key is task name as string
# value is dictionary with keys in ['task', 'depends', 'help', 'description']
# where value['task'] is the task function reference, value['depends'] is a list of string task names that
# are this task's dependencies, value['help'] is None or a string, and value['description'] is the task's docstring.
HerringTasks = {}


class TaskWithArgs(object):
    """
    Task decorator

    This gathers info about the task and stores it into the
    HerringApp.HerringTasks dictionary.  The decorator does not run the
    task.  The task will be invoked via the HerringApp.HerringTasks
    dictionary.

    """

    # the unused command line arguments are placed here as a list so
    # that tasks can access them as: task.argv or task.kwargs
    argv = None
    kwargs = None

    # noinspection PyRedeclaration
    def __init__(self, *deco_args, **deco_kwargs):
        """
        keyword arguments:
            depends:  a list of task names where the task names are strings
            help: a brief task note, usually command line options the task accepts
        """
        self.deco_args = deco_args
        self.deco_kwargs = deco_kwargs
        self._settings = None

    def __call__(self, func):
        """
        Invoked once when the module is loaded so we hook in here
        to build our internal task dictionary.

        :param func: the function being decorated
        :returns: function that simply invokes the decorated function
        """
        depends = []
        if 'depends' in self.deco_kwargs:
            depends = self.deco_kwargs['depends']

        task_help = None
        if 'help' in self.deco_kwargs:
            task_help = self.deco_kwargs['help']

        def _wrap(*args, **kwargs):
            """
            A simple wrapper

            :param args: positional arguments passed through
            :param kwargs: keyword arguments passed through
            """
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                tb = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                fatal("{name} - ERROR: {err}\n{tb}".format(name=func.__name__, err=str(ex), tb=tb))

        # save task info into HerringTasks
        HerringTasks[func.__name__] = {
            'task': _wrap,
            'depends': depends,
            'help': task_help,
            'description': func.__doc__
        }
        return _wrap
