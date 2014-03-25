# coding=utf-8
"""
A context manager base class that optionally reads a config file then uses the values as defaults
for command line argument parsing.

To be useful, you must derive a class from this base class and you should override at least the **_cli_options** method.
You may find it useful to also override **_config_files** and **_cli_validate** methods.

This base class adds the following features to ArgumentParser:

* config file support from either the command line (-c|--conf_file FILE) or from expected locations (current
  directory then user's home directory).  The default config file name is created by prepending '.' and appending
  'rc' to the applications package name (example, app_package = 'foobar', then config file name would be
  '.foobarrc' and the search order would be: ['./.foobarrc', '~/.foobarrc'].

* display the application's version from app_package.version (usually defined in app_package/__init__.py).

* display the application's longhelp which is the module docstring in app_package/__init__.py.
"""
try:
    from ConfigParser import ConfigParser, NoSectionError
except ImportError:
    from configparser import ConfigParser, NoSectionError

import herring
from herring.support.simple_logger import info

__docformat__ = 'restructuredtext en'

import os
import re
import argparse

__all__ = ("ApplicationSettings",)


class ApplicationSettings(object):
    """
    Usage::

        class MySettings(ApplicationSettings):
            HELP = {
                'foo': 'the foo option',
                'bar': 'the bar option',
            }

            def __init__(self):
                super(MySettings, self).__init__('App Name', 'app_package', ['APP Section'], self.HELP)

            def _cli_options(parser):
                parser.add_argument('--foo', action='store_true', help=self._help['foo'])
                parser.add_argument('--bar', action='store_true', help=self._help['bar'])

    Context Manager Usage::

        with MySettings() as settings:
            if settings.foo:
                pass

    Traditional Usage::

        parser, settings = MySettings().parse()
        if settings.foo:
            pass
    """

    VERSION_REGEX = r'__version__\s*=\s*[\'\"](\S+)[\'\"]'

    def __init__(self, app_name, app_package, config_sections, help_strings):
        """
        :param str app_name: The application name
        :param app_package: The application's package name
        :type app_package: str
        :param config_sections: The INI sections in the config file to import in as defaults to the argument parser.
        :type config_sections: list
        :param help_strings: A dictionary that maps argument names to the argument's help message.
        :type help_strings: dict
        """
        self.__app_name = app_name
        self.__app_package = app_package
        self.__config_sections = config_sections
        self._parser = None
        self._settings = None
        self._remaining_argv = None

        default_help = {
            'version': "Show the application's version.  (default: %(default)s)",
            'longhelp': 'Verbose help message.  (default: %(default)s)',
        }

        self._help = default_help.copy()
        self._help.update(help_strings.copy())

    def parse(self):
        """
        Perform the parsing of the optional config files and the command line arguments.

        :return: the parser and the settings
        :rtype: tuple(argparse.ArgumentParser, argparse.Namespace)
        """
        config_parser_help = 'Configuration file in INI format (default: {files})'.format(files=self._config_files())
        conf_parser = argparse.ArgumentParser(add_help=False)
        conf_parser.add_argument('-c', '--conf_file', metavar='FILE', help=config_parser_help)

        args, remaining_argv = conf_parser.parse_known_args()

        config_files = self._config_files()[:]
        if args.conf_file:
            config_files.insert(0, args.conf_file)

        config = ConfigParser()
        config.read(config_files)
        defaults = {}
        for section in self.__config_sections:
            try:
                defaults.update(dict(config.items(section)))
            except NoSectionError:
                pass

        parser = argparse.ArgumentParser(self.__app_name,
                                         parents=[conf_parser],
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         description=self._help[self.__app_name])

        parser.set_defaults(**defaults)

        self._cli_options(parser)
        settings, leftover_argv = parser.parse_known_args(remaining_argv)

        return parser, settings, leftover_argv

    def _config_files(self):
        """
        Defines the default set of config files to try to use.  The set is ".{__app_package}rc" in the current
        directory and in the user's home directory.

        You may override this method if you want to use a different set of config files.

        :return: the set of config file locations
        :rtype: list
        """
        rc_name = ".{pkg}rc".format(pkg=self.__app_package)
        conf_name = os.path.expanduser("~/.{pkg}/{pkg}.conf".format(pkg=self.__app_package))
        home_rc_name = os.path.expanduser("~/.{pkg}rc".format(pkg=self.__app_package))
        return [rc_name, conf_name, home_rc_name]

    def _cli_options(self, parser):
        """
        This is where you should add arguments to the parser.

        You should override this method.

        :param parser: the argument parser with --conf_file already added.
        :type parser: argparse.ArgumentParser
        """
        parser.add_argument('-v', '--version',
                            dest='version',
                            action='store_true',
                            help=self._help['version'])

        parser.add_argument('--longhelp',
                            dest='longhelp',
                            action='store_true',
                            help=self._help['longhelp'])

    def _cli_validate(self, settings):
        """
        This provides a hook for validating the settings after the parsing is completed.

        :param settings: the settings object returned by ArgumentParser.parse_args()
        :type settings: argparse.Namespace
        :return: the error message if any
        :rtype: str or None
        """
        return None

    def __enter__(self):
        """
        context manager enter
        :return: the settings namespace
        :rtype: argparse.Namespace
        """
        self._parser, self._settings, self._remaining_argv = self.parse()

        # Logger.set_verbose(not self._settings.quiet)
        # Logger.set_debug(self._settings.debug)

        if self._settings.longhelp:
            info(herring.__doc__)
            exit(0)

        if self._settings.version:
            info("Version %s" % self._load_version())
            exit(0)

        error_message = self._cli_validate(self._settings)
        if error_message is not None:
            self._parser.error("\n" + error_message)

        return self._settings

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        context manager exit
        """
        pass

    def _load_version(self):
        r"""
        Get the version from __init__.py with a line::

            /^__version__\s*=\s*(\S+)/

        If it doesn't exist try to load it from the VERSION.txt file.

        If still no joy, then return '0.0.0'

        :returns: the version string or 'Unknown'
        :rtype: str
        """

        # noinspection PyBroadException
        try:
            return __import__(self.__app_package).__version__
        except:
            pass

        path = os.path.dirname(__file__)
        print("_load_version path=>%s" % path)

        # trying __init__.py first
        try:
            file_name = os.path.join(path, '__init__.py')
            with open(file_name, 'r') as in_file:
                for line in in_file.readlines():
                    match = re.match(self.VERSION_REGEX, line)
                    if match:
                        return match.group(1)
        except IOError:
            pass

        # no joy, so try getting the version from a deprecated VERSION.txt file.
        try:
            # noinspection PyUnresolvedReferences
            file_name = os.path.join(path, 'VERSION.txt')
            with open(file_name, 'r') as in_file:
                return in_file.read().strip()
        except IOError:
            pass

        # no joy again, so return default
        return 'Unknown'

    def help(self):
        """
        Let the parser print the help message.

        :return: 2
        :rtype: int
        """
        if self._parser:
            self._parser.print_help()
        return 2