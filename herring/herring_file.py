# coding=utf-8

"""
Provides built in run support methods for herringfile tasks.
"""
__docformat__ = 'restructuredtext en'

__all__ = ('HerringFile',)


# noinspection PyPep8Naming
class HerringFile(object):
    """Run helper"""
    directory = ''
    settings = None
    herringlib_paths = []

    uninstalled_packages = []
    installed_packages = None
