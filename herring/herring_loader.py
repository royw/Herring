# coding=utf-8

"""
Describe Me!
"""
import os
from pprint import pformat
import tempfile

import shutil

import sys

from herring.herring_file import HerringFile
from herring.support.mkdir_p import mkdir_p
from herring.support.path import Path
from herring.support.simple_logger import info, debug
from herring.support.utils import find_files
from herring.support.list_helper import unique_list

__docformat__ = 'restructuredtext en'
__author__ = 'wrighroy'


# noinspection PyMethodMayBeStatic
class HerringLoader(object):
    def __init__(self, settings):
        """
        The Herring application.

        :param settings: the application settings
        :type settings: HerringSettings
        """
        # noinspection PyArgumentEqualDefault
        self.settings = settings
        self.__sys_path = sys.path[:]
        self.union_dir = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.union_dir is not None and not self.settings.leave_union_dir:
            # noinspection PyTypeChecker
            shutil.rmtree(os.path.dirname(self.union_dir))

    def load_tasks(self, herringfile):
        """
        Loads the given herringfile then loads any herringlib files.

        :param herringfile: the herringfile path
        :type herringfile: str
        :return: None
        """

        herringfile_path = Path(herringfile).parent
        library_paths = self._locate_library(herringfile_path, self.settings)

        if len(library_paths) == 1:
            self._load_modules(herringfile, [Path(library_paths[0])])
        else:
            self.union_dir = mkdir_p(os.path.join(tempfile.mkdtemp(), 'herringlib'))
            for src_dir in [os.path.abspath(str(path)) for path in reversed(library_paths)]:
                if not self.settings.json:
                    info("src_dir: %s" % src_dir)
                for src_root, dirs, files in os.walk(src_dir):
                    files = [f for f in files if not (f[0] == '.' or f.endswith('.pyc'))]
                    dirs[:] = [d for d in dirs if not (d[0] == '.' or d == '__pycache__')]
                    rel_root = os.path.relpath(src_root, start=src_dir)
                    dest_root = os.path.join(self.union_dir, rel_root)
                    mkdir_p(dest_root)
                    for basename in [name for name in files]:
                        src_name = os.path.join(src_root, basename)
                        dest_name = os.path.join(dest_root, basename)
                        try:
                            shutil.copy(src_name, dest_name)
                        except shutil.Error:
                            pass

            self._load_modules(herringfile, [Path(self.union_dir)])

    def _load_modules(self, herringfile, library_paths):
        """

        :param herringfile:
        :type herringfile:
        :param library_paths:
        :type library_paths: list[Path]
        :return:
        :rtype:
        """
        herringfile_path = Path(herringfile).parent
        debug("library_paths: %s" % repr(library_paths))
        HerringFile.herringlib_paths = [str(path.parent) for path in library_paths
                                        if path.parent != herringfile_path] + [str(herringfile_path)]
        sys.path = unique_list(HerringFile.herringlib_paths + self.__sys_path[:])

        for path in HerringFile.herringlib_paths:
            debug("herringlib path: %s" % path)
        debug(pformat("sys.path: %s" % repr(sys.path)))

        try:
            self._load_file(herringfile)
        except ImportError as ex:
            debug(str(ex))
            debug('failed to import herringfile')

        try:
            __import__('herringlib')
            debug('imported herringlib')
        except ImportError as ex:
            debug(str(ex))
            debug('failed to import herringlib')

        for lib_path in library_paths:
            sys.path = [lib_path] + self.__sys_path
            debug("sys.path: %s" % repr(sys.path))
            for file_name in self.library_files(library_paths=[lib_path]):
                mod_name = 'herringlib.' + Path(file_name).stem
                try:
                    __import__(mod_name)
                    debug('imported {name}'.format(name=mod_name))
                except ImportError as ex:
                    debug(str(ex))
                    debug('failed to import {name}'.format(name=mod_name))

        sys.path = self.__sys_path[:]

    def _locate_library(self, herringfile_path, settings):
        """
        locate and validate the paths to the herringlib directories

        :param settings: the application settings
        :param herringfile_path: the herringfile path
        :type herringfile_path: str
        :return: library path
        :rtype: list(Path)
        """
        paths = []
        for lib_path in [Path(os.path.expanduser(lib_dir)) for lib_dir in settings.herringlib]:
            if not lib_path.is_absolute():
                lib_path = Path(herringfile_path, str(lib_path))
            if lib_path.is_dir():
                paths.append(lib_path)
        return paths

    @staticmethod
    def library_files(library_paths=None, pattern='*.py'):
        """
        Yield any .py files located in herringlib subdirectory in the
        same directory as the given herringfile.  Ignore package __init__.py
        files, .svn and templates sub-directories.

        :param library_paths: the path to the herringlib directory
        :type library_paths: list(Path)
        :param pattern: the file pattern (glob) to select
        :type pattern: str
        :return: iterator for path to a library herring file
        :rtype: iterator[str]
        """
        if library_paths is None:
            return
        for lib_path in library_paths:
            debug("lib_path: {path}".format(path=lib_path))
            parent_path = lib_path.parent
            if lib_path.is_dir():
                files = find_files(str(lib_path), excludes=['*/templates/*', '.svn'], includes=[pattern])
                for file_path in [Path(file_name) for file_name in files]:
                    if file_path.name == '__init__.py':
                        continue
                    debug("parent_path: %s" % str(parent_path))
                    debug("loading from herringlib:  %s" % file_path)
                    rel_path = file_path.relative_to(parent_path)
                    debug("relative path: %s" % str(rel_path))
                    yield rel_path

    def _load_plugin(self, plugin, paths):
        """load a plugin module if we haven't yet loaded it
        :param plugin: the herringlib plugin to load
        :param paths: the herringlib path
        """
        # check if we haven't loaded it already
        try:
            return sys.modules[plugin]
        except KeyError:
            pass
        # ok not found so load it
        debug("_load_plugin({plugin}, {paths})".format(plugin=plugin, paths=paths))

        try:
            # python3
            # noinspection PyUnresolvedReferences,PyCompatibility
            from importlib import import_module

            package = 'herringlib'
            import_module(package)
            mod = import_module(plugin, package)
        except ImportError:
            # python2
            from imp import load_module, PY_SOURCE

            filename = os.path.join(paths, plugin)
            extension = os.path.splitext(filename)[1]
            mode = 'r'
            desc = (extension, mode, PY_SOURCE)
            debug(repr(desc))
            with open(filename, mode) as fp:
                mod = load_module(plugin, fp, filename, desc)
        return mod

    def _load_file(self, file_name):
        """
        Loads the tasks from the herringfile populating the
        HerringApp.HerringTasks structure.

        :param file_name: the herringfile
        :type file_name: str
        :return: None
        """
        plugin = os.path.basename(file_name)
        path = os.path.dirname(file_name)
        debug("plugin: {plugin}, path: {path}".format(plugin=plugin, path=path))
        self._load_plugin(plugin, path)
