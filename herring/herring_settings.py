# coding=utf-8

"""
HarvesterSettings adds application specific information to the generic ApplicationSettings class.
"""
import os
import textwrap
import io

from herring.support.mkdir_p import mkdir_p
from herring.support.simple_logger import warning
from herring.support.application_settings import ApplicationSettings

__docformat__ = 'restructuredtext en'
__all__ = ("HerringSettings",)

DEFAULT_HERRINGLIB = '~/.herring/herringlib'
DEFAULT_HERRINGCONF = '~/.herring/herring.conf'


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
        'herringlib': 'The location of the herringlib directory to use (default: {dirs}).',

        'task_group': '',
        'list_tasks': 'Lists the public tasks (with docstrings).',
        'list_task_usages': 'Shows the full docstring for the tasks (with docstrings).',
        'list_dependencies': 'Lists the tasks (with docstrings) with their '
                             'dependencies.',
        'tasks': "The tasks to run.  If none specified, tries to run the "
                 "'default' task.",

        'task_options_group': '',
        'list_all_tasks': 'Lists all tasks, even those without docstrings.',
        'interactive': 'Run all the tasks in the same process without buffering the output.  The '
                       'default action is to run the tasks in parallel processes, buffering each tasks '
                       'output',

        'output_group': '',
        'quiet': 'Suppress herring output.',
        'debug': 'Display task debug messages.',
        'herring_debug': 'Display herring debug messages.',
        'leave_union_dir': 'Leave the union herringlib directory on disk (do not automatically erase).  '
                           'Useful for debugging.',
        'json': 'Output list tasks (--tasks, --usage, --depends, --all) in JSON format.',

        'info_group': '',
        'version': "Show herring's version.",
        'longhelp': 'Long help about Herring.',
        'environment': "Show herring's environment",
    }

    def __init__(self, default_herringlib=DEFAULT_HERRINGLIB, default_herringconf=DEFAULT_HERRINGCONF):
        super(HerringSettings, self).__init__('Herring', 'herring', ['Herring'], self.HELP)
        self._herringlib_path = ['herringlib']
        if 'HERRINGLIB' in os.environ:
            self._herringlib_path.append(os.environ['HERRINGLIB'])
        self._herringlib_path.append(default_herringlib)

        herring_conf = os.path.expanduser(default_herringconf)
        if not os.path.isfile(herring_conf):
            self._create_herring_conf_file(herring_conf)

    # noinspection PyMethodMayBeStatic
    def _create_herring_conf_file(self, herring_conf):
        herring_conf_dir = os.path.dirname(herring_conf)
        mkdir_p(herring_conf_dir)
        user = os.getenv('USER', 'nobody')
        email = '{user}@localhost'.format(user=user)
        try:
            with io.open(herring_conf, 'w', encoding="utf-8") as conf_file:
                conf_file.write(textwrap.dedent(u"""\
                [Herring]

                [project]
                author: {author}
                author_email: {email}
                dist_host: localhost
                pypi_path: /var/pypi/dev
                """.format(author=user, email=email)))
        except IOError as ex:
            warning("Could not create ~/.herring/herring.conf ({file}) - {err}".format(file=herring_conf,
                                                                                       err=str(ex)))

    def _cli_options(self, parser, defaults):
        """
        This is where you should add arguments to the parser.

        You should override this method.

        :param parser: the argument parser with --conf_file already added.
        :type parser: argparse.ArgumentParser
        :param defaults: the default dictionary usually loaded from a config file
        :type defaults: dict(str,str)
        """
        config_group = parser.add_argument_group(title="Config Group", description=self._help['config_group'])
        config_group.add_argument('-f', '--herringfile', metavar='FILESPEC',
                                  default='herringfile', help=self._help['herringfile'])
        config_group.add_argument('--herringlib', metavar='DIRECTORY', nargs='*', default=self._herringlib_path,
                                  help=self._help['herringlib'].format(dirs=self._herringlib_path))

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
        task_options_group.add_argument('-i', '--interactive', dest='interactive', action='store_true',
                                        default=False, help=self._help['interactive'])

        output_group = parser.add_argument_group(title='Output Options', description=self._help['output_group'])
        output_group.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                                  help=self._help['quiet'])
        output_group.add_argument('-d', '--debug', dest='debug',
                                  action='store_true', help=self._help['debug'])
        output_group.add_argument('--herring_debug', dest='herring_debug',
                                  action='store_true', help=self._help['herring_debug'])
        output_group.add_argument('--leave_union_dir', action='store_true', help=self._help['leave_union_dir'])
        output_group.add_argument('-j', '--json', dest='json', action='store_true',
                                  help=self._help['json'])

        info_group = parser.add_argument_group(title='Informational Commands', description=self._help['info_group'])
        info_group.add_argument('-v', '--version', dest='version',
                                action='store_true', help=self._help['version'])
        info_group.add_argument('-l', '--longhelp', dest='longhelp', action='store_true',
                                help=self._help['longhelp'])
        info_group.add_argument('--environment', action='store_true', help=self._help['environment'])

    # noinspection PyUnresolvedReferences
    def _cli_validate(self, settings, remaining_argv):
        """
        Verify we have required options for commands.  For example, get_log and reset_log require
        DUT credentials.

        :param settings: the settings object returned by ArgumentParser.parse_args()
        :type settings: argparse.Namespace
        :return: the error message if any
        :rtype: str or None
        """
        return None
