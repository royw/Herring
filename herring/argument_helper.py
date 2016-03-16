# coding=utf-8

"""
Helper for handling command line arguments.
"""

from collections import deque

__docformat__ = 'restructuredtext en'
__all__ = ('ArgumentHelper',)


class ArgumentHelper(object):
    """ Helper for handling command line arguments. """

    @staticmethod
    def argv_to_dict(argv):
        """
        Given a list of keyword arguments, parse into a kwargs dictionary.

        Each argument should either start with '--' indicating a key, or not,
        indicating a value.
        Also supports "--key=value" syntax.
        True will be used for the value of a key that does not have a given
        value. Multiple values will be joined with a space.

        This method does not attempt to cast any values, they all remain
        strings.

        >>> argv = ['--flag', 'false', '--foo', 'alpha', 'beta', '--bar=delta', '--charlie']
        >>> kwargs = ArgumentHelper.argv_to_dict(argv)
        >>> kwargs
        {'charlie': True, 'flag': 'false', 'foo': 'alpha beta', 'bar': 'delta'}

        :param argv: argument list
        :type argv: list
        """
        kwargs = {}
        current_key = None
        args = deque(argv)
        while args:
            arg = args.popleft()
            if arg == '--':
                ArgumentHelper.set_kwargs_flag(kwargs, current_key)
            elif arg.startswith('--'):
                ArgumentHelper.set_kwargs_flag(kwargs, current_key)
                current_key = arg[2:]
                if '=' in current_key:
                    current_key, value = current_key.split("=", 1)
                    kwargs[current_key] = value
            else:
                ArgumentHelper.merge_kwargs(kwargs, current_key, arg)
        ArgumentHelper.set_kwargs_flag(kwargs, current_key)
        return kwargs

    @staticmethod
    def set_kwargs_flag(kwargs, key):
        """
        set the flag in kwargs if it has not yet been set.

        :param kwargs: keyword arguments
        :type kwargs: dict
        :param key: key
        :type key: str
        """
        if key is not None:
            if key not in kwargs:
                kwargs[key] = True

    @staticmethod
    def merge_kwargs(kwargs, key, value):
        """
        set the kwargs key/value pair, joining any pre-existing value with
        a space.

        :param kwargs: keyword arguments
        :type kwargs: dict
        :param key: key
        :type key: str
        :param value: the value to set the kwarg to
        :type value: object
        """
        if key is not None:
            if key in kwargs:
                value = ' '.join([kwargs[key], value])
            kwargs[key] = value
