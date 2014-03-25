# coding=utf-8

"""
HarvesterSettings adds application specific information to the generic ApplicationSettings class.
"""
import textwrap

__docformat__ = 'restructuredtext en'

from herring.support.application_settings import ApplicationSettings

__all__ = ("HarvesterSettings",)


class HerringSettings(ApplicationSettings):
    """
    Defines the command line arguments to parse.
    """
    HELP = {
        'Herring': textwrap.dedent("""\
        "Then, you must cut down the mightiest tree in the forrest... with... a herring!"

        Herring is a simple python make utility.  You write tasks in python, and
        optionally assign dependent tasks.  The command line interface lets you
        easily list the tasks and run them.  See --longhelp for details.
        """),

        'config_group': '',
        'herringfile': 'The herringfile name to use, by default uses "herringfile".',
        'herringlib': 'The location of the herringlib directory to use.',
        'config_file': 'The location of the config file to use',

        'task_group': '',
        'list_tasks': 'Lists the tasks (with docstrings) in the herringfile.',
        'list_task_usages': 'Shows the full docstring for the tasks (with docstrings) in the herringfile.',
        'list_dependencies': 'Lists the tasks (with docstrings) with their '
                             'dependencies in the herringfile.',
        'tasks': "The tasks to run.  If none specified, tries to run the "
                 "'default' task.",

        'task_options_group': '',
        'list_all_tasks': 'Lists all tasks, even those without docstrings.',

        'output_group': '',
        'quiet': 'Suppress herring output.',
        'debug': 'Display debug messages.',
        'json': 'Output list tasks (--tasks, --usage, --depends, --all) in JSON format.',

        'info_group': '',
        'version': "Show herring's version.",
        'longhelp': 'Long help about Herring.',
    }

    def __init__(self):
        super(HerringSettings, self).__init__('Herring', 'herring', ['Herring'], self.HELP)

    def _cli_options(self, parser):
        """
        Adds application specific arguments to the parser.

        :param parser: the argument parser with --conf_file already added.
        :type parser: argparse.ArgumentParser
        """
        config_group = parser.add_argument_group(title="Config Group", description=self._help['config_group'])
        config_group.add_argument('-f', '--herringfile', metavar='FILESPEC',
                                  default='herringfile', help=self._help['herringfile'])
        config_group.add_argument('--herringlib', metavar='DIRECTORY', help=self._help['herringlib'])
        config_group.add_argument('--config_file', metavar='FILESPEC', help=self._help['config_file'])

        task_group = parser.add_argument_group(title='Task Commands', description=self._help['task_group'])
        task_group.add_argument('-T', '--tasks', dest='list_tasks',
                                action="store_true", help=self._help['list_tasks'])
        task_group.add_argument('-U', '--usage', dest='list_task_usages',
                                action="store_true", help=self._help['list_task_usages'])
        task_group.add_argument('-D', '--depends', dest='list_dependencies',
                                action="store_true", help=self._help['list_dependencies'])
        task_group.add_argument('tasks', nargs='*', help=self._help['tasks'])

        task_options_group = parser.add_argument_group(title='Task Options',
                                                       description=self._help['task_options_group'])
        task_options_group.add_argument('-a', '--all', dest='list_all_tasks',
                                        action='store_true', help=self._help['list_all_tasks'])

        output_group = parser.add_argument_group(title='Output Options', description=self._help['output_group'])
        output_group.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                                  help=self._help['quiet'])
        output_group.add_argument('-d', '--debug', dest='debug',
                                  action='store_true', help=self._help['debug'])
        output_group.add_argument('-j', '--json', dest='json', action='store_true',
                                  help=self._help['json'])

        info_group = parser.add_argument_group(title='Informational Commands', description=self._help['info_group'])
        info_group.add_argument('-v', '--version', dest='version',
                                action='store_true', help=self._help['version'])
        info_group.add_argument('-l', '--longhelp', dest='longhelp', action='store_true',
                                help=self._help['longhelp'])

    # noinspection PyUnresolvedReferences
    def _cli_validate(self, settings):
        """
        Verify we have required options for commands.  For example, get_log and reset_log require
        DUT credentials.

        :param settings: the settings object returned by ArgumentParser.parse_args()
        :type settings: argparse.Namespace
        :return: the error message if any
        :rtype: str or None
        """
        return None