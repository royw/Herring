# coding=utf-8

"""
Provides support for the @task decorator.
"""
import os
import traceback
import sys

__docformat__ = 'restructuredtext en'

from herring.support.simple_logger import fatal

__all__ = ('TaskWithArgs', 'HerringTasks', 'NameSpace')


# HerringTasks dictionary
# key is task name as string
# value is dictionary with keys in ['task', 'depends', 'help', 'description', 'kwargs']
# where value['task'] is the task function reference, value['depends'] is a list of string task names that
# are this task's dependencies, value['help'] is None or a string, and value['description'] is the task's docstring.
HerringTasks = {}

name_spaces = []


class NameSpace(object):
    """
    Context manager for task namespaces.

    Usage::

        with namespace('foo', 'bar'):
            @task()
            def alpha():
                \"""alpha\"""
                pass

            with namespace('mucho'):
                @task()
                def bravo():
                    \"""bravo\"""
                    pass

    should give you the following tasks::

    * foo::bar::alpha
    * foo::bar::mucho::bravo
    """
    def __init__(self, *namespaces):
        self.names = namespaces

    def __enter__(self):
        global name_spaces
        name_spaces.extend(self.names)
        return self

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, exc_val, exc_tb):
        global name_spaces
        name_spaces = [x for x in name_spaces if x not in self.names]


# noinspection PyMethodMayBeStatic
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
    argv = []
    kwargs = {}

    def os_path_split_asunder(self, path):
        """
        Split a path into a list of component parts.

        From: http://stackoverflow.com/questions/4579908/cross-platform-splitting-of-path-in-python

        :param path: A file path (unix or windows)
        :type path: str
        :returns: the path components (i.e., 'a/b/c' => ['a', 'b', 'c']
        :rtype: list
        """
        parts = []
        while True:
            newpath, tail = os.path.split(path)
            if newpath == path:
                assert not tail
                if path:
                    parts.append(path)
                break
            parts.append(tail)
            path = newpath
        parts.reverse()
        return parts

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
        global name_spaces
        self.namespace = "::".join(name_spaces)

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

        private = False
        if 'private' in self.deco_kwargs:
            if self.deco_kwargs['private'] in [True, 'True', 'true']:
                private = True

        if self.namespace:
            depends = [self.namespace + '::' + name for name in depends]

        task_help = None
        if 'help' in self.deco_kwargs:
            task_help = self.deco_kwargs['help']

        task_kwargs = None
        if 'kwargs' in self.deco_kwargs:
            task_kwargs = self.deco_kwargs['kwargs']

        name_space = self.namespace
        if 'namespace' in self.deco_kwargs:
            name_space = self.deco_kwargs['namespace']

        full_name = func.__name__
        if name_space:
            full_name = name_space + '::' + func.__name__

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
                fatal("{name} - ERROR: {err}\n{tb}".format(name=func.__name__,
                                                           err=str(ex),
                                                           tb=tb))

        # save task info into HerringTasks
        HerringTasks[full_name] = {
            'task': _wrap,
            'depends': depends,
            'private': private,
            'help': task_help,
            'description': func.__doc__,
            'namespace': name_space,
            'fullname': full_name,
            'name': func.__name__,
            'kwargs': task_kwargs
        }
        # debug("HerringTasks[{name}]: {value}".format(name=full_name, value=repr(HerringTasks[full_name])))
        return _wrap
