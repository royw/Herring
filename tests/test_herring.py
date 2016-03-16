# coding=utf-8

"""
Test the herring application.
"""
import os
import shutil
from tempfile import mkdtemp
from unittest import TestCase

from herring.herring_loader import HerringLoader
from herring.herring_runner import HerringRunner
from herring.support.path import Path

try:
    # noinspection PyCompatibility
    from io import StringIO
except ImportError:
    # noinspection PyCompatibility
    from StringIO import StringIO

from herring.argument_helper import ArgumentHelper
from herring.herring_app import HerringApp
from herring.herring_cli import HerringCLI
from herring.support.simple_logger import Logger


def dummy_task():
    """ dummy method for our herring_tasks mock """
    pass


# noinspection PyPep8Naming
class TestHerring(TestCase):
    """
    Test suite for Herring application
    """

    def setUp(self):
        """ ran before each test """
        self.herring_tasks = {
            'alpha': {'task': dummy_task, 'depends': []},
            'beta': {'task': dummy_task, 'depends': []},
            'gamma': {'task': dummy_task, 'depends': ['alpha']},
            'delta': {'task': dummy_task, 'depends': ['beta', 'phi']},
            'phi': {'task': dummy_task, 'depends': []},
            'sigma': {'task': dummy_task, 'depends': ['alpha', 'delta']}
        }
        self._output_buf = StringIO()
        Logger.log_outputter = {
            'debug': [],
            'info': [self._output_buf],
            'warning': [self._output_buf],
            'error': [self._output_buf],
            'fatal': [self._output_buf],
        }

        self.herring_cli = HerringCLI()
        self.herring_app = HerringApp()

    def test__tasksToDependDict(self):
        """
        verify that _tasksToDependDict creates the correct data structure
        """

        # noinspection PyProtectedMember
        dataDict = HerringRunner()._tasks_to_depend_dict(self.herring_tasks.keys(), self.herring_tasks)
        self.assertEqual(dataDict['alpha'], set([]))
        self.assertEqual(dataDict['beta'], set([]))
        self.assertEqual(dataDict['gamma'], set(['alpha']))
        self.assertEqual(dataDict['delta'], set(['beta', 'phi']))
        self.assertEqual(dataDict['phi'], set([]))
        self.assertEqual(dataDict['sigma'], set(['alpha', 'delta']))
        self.assertFalse(self._output_buf.getvalue())

    def verify_findDependencies(self, src_list, dest_list):
        """
        helper for testing _find_dependencies

        :param src_list: source list containing task names
        :param dest_list: output list containing task names
        """
        # noinspection PyProtectedMember
        depends = HerringRunner()._find_dependencies(src_list, self.herring_tasks)
        self.assertEqual(depends, dest_list)

    def test__find_dependencies(self):
        """ tasks are unordered """
        self.verify_findDependencies(['alpha'], ['alpha'])
        self.verify_findDependencies(['beta'], ['beta'])
        self.verify_findDependencies(['gamma'], ['gamma', 'alpha'])
        self.verify_findDependencies(['delta'], ['delta', 'beta', 'phi'])
        self.verify_findDependencies(['phi'], ['phi'])
        self.verify_findDependencies(['sigma'], ['sigma', 'alpha', 'delta', 'beta', 'phi'])

    def verify_resolveDependencies(self, src_list, dest_list):
        """
        helper for testing _resolveDependencies

        :param src_list: source list containing task names
        :param dest_list: output list containing task names
        """
        # noinspection PyProtectedMember
        depends = HerringRunner()._resolve_dependencies(src_list, self.herring_tasks)
        for index, dependent in enumerate(depends):
            self.assertEqual(set(dependent), set(dest_list[index]))

    def test__resolveDependencies(self):
        """ tasks are ordered """
        self.verify_resolveDependencies(['alpha'], [['alpha']])
        self.verify_resolveDependencies(['beta'], [['beta']])
        self.verify_resolveDependencies(['gamma'], [['alpha'], ['gamma']])
        self.verify_resolveDependencies(['delta'], [['beta', 'phi'], ['delta']])
        self.verify_resolveDependencies(['phi'], [['phi']])
        self.verify_resolveDependencies(['sigma'], [['phi', 'beta', 'alpha'], ['delta'], ['sigma']])

    # def test__wrap(self):
    #     """ verify the _wrap method correctly wraps strings """
    #     quotes = """
    #     "Strange women lying in ponds distributing swords is no basis for a system of government!"
    #     "-She turned me into a newt!
    #     -A newt?
    #     -I got better..."
    #     "We are no longer the knights who say ni! We are now the knights who say ekki-ekki-ekki-pitang-zoom-boing!"
    #     "Nudge, nudge, wink, wink. Know what I mean?"
    #     "And the Lord spake, saying, "First shalt thou take out the Holy Pin. Then shalt thou count to three,
    # no more, no less. Three shall be the number thou shalt count, and the number of the counting shall be three.
    # Four shalt thou not count, neither count thou two, excepting that thou then proceed to three. Five is right out
    # . Once the number three, being the third number, be reached, then lobbest thou thy Holy Hand Grenade of Antioch
    #  towards thy foe, who, being naughty in my sight, shall snuff it."
    #     "Jesus did. I was hopping along, when suddenly he comes and cures me. One minute I'm a leper with a trade,
    # next moment me livelihood's gone. Not so much as a by your leave. Look. I'm not saying that being a leper was a
    #  bowl of cherries. But it was a living. I mean, you try waving muscular suntanned limbs in people's faces
    # demanding compassion. It's a bloody disaster."
    #     "The Castle Aaahhhgggg - our quest is at an end."
    #     """
    #
    #     for width in range(40, 80):
    #         lines = self.herring_cli._wrap(quotes, width).split("\n")
    #         for line in lines:
    #             line_length = len(line)
    #             self.assertTrue(line_length <= width,
    #                             "line length(%d) <= %d, line=\"%s\"" %
    #                             (line_length, width, line))

    def test_argvToDict_empty(self):
        """test with no arguments"""
        self.assertEqual(ArgumentHelper.argv_to_dict([]), {})

    def test_argvToDict_flag(self):
        """test with just a single flag argument"""
        self.assertEqual(ArgumentHelper.argv_to_dict(['--flag']),
                         {'flag': True})

    def test_argvToDict_pair(self):
        """test with just a single key value pair of arguments"""
        self.assertEqual(ArgumentHelper.argv_to_dict(['--foo', 'bar']),
                         {'foo': 'bar'})

    def test_argvToDict_mixed(self):
        """test with a mixture of arguments"""
        argv = ['--flag', 'false',
                '--foo', 'alpha', 'beta',
                '--bar', 'delta',
                '--charlie']
        expected_kwargs = {'charlie': True,
                           'flag': 'false',
                           'foo': 'alpha beta',
                           'bar': 'delta'}
        kwargs = ArgumentHelper.argv_to_dict(argv)
        self.assertEqual(kwargs, expected_kwargs)

    def test_argvToDict_value(self):
        """test with just a single value, i.e., no key argument"""
        self.assertEqual(ArgumentHelper.argv_to_dict(['fubar']), {})
        self.assertEqual(ArgumentHelper.argv_to_dict(['-fubar']), {})

    def test_argvToDict_doubleHyphens(self):
        """test with just a -- argument"""
        self.assertEqual(ArgumentHelper.argv_to_dict(['--']), {})

    def test_argvToDict_doubleHyphensEnd(self):
        """test with multiple arguments where the last argument is --"""
        self.assertEqual(ArgumentHelper.argv_to_dict(['--flag', '--']),
                         {'flag': True})

    def test_argvToDict_doubleHyphensBegin(self):
        """test with multiple arguments where the first argument is --"""
        self.assertEqual(ArgumentHelper.argv_to_dict(['--', '--flag']),
                         {'flag': True})

    def test_argvToDict_doubleHyphensMiddle(self):
        """
        test with multiple arguments where -- is in the middle of the arguments
        """
        argv = ['--flag', 'false',
                '--',
                '--foo', 'alpha', 'beta',
                '--bar', 'delta',
                '--charlie']
        expected_kwargs = {'charlie': True,
                           'flag': 'false',
                           'foo': 'alpha beta',
                           'bar': 'delta'}
        kwargs = ArgumentHelper.argv_to_dict(argv)
        self.assertEqual(kwargs, expected_kwargs)

    def test_argvToDict_singleHyphens(self):
        """
        test improperly using single hyphens when the user probably meant double
        hyphens
        """
        argv = ['-flag', 'false',
                '-',
                '-foo', 'alpha', 'beta',
                '-bar', 'delta', '-charlie']
        kwargs = ArgumentHelper.argv_to_dict(argv)
        self.assertEqual(kwargs, {})

    def test_argvToDict_equals(self):
        """test the --key=value syntax"""
        self.assertEqual(ArgumentHelper.argv_to_dict(['--foo=bar']),
                         {'foo': 'bar'})

    def test_argvToDict_doubleEquals(self):
        """test more than one equal sign in a key argument"""
        self.assertEqual(ArgumentHelper.argv_to_dict(['--foo=bar=alpha']),
                         {'foo': 'bar=alpha'})

    def test_library_files(self):
        """
        creates temp file structure then tests if library_files can find
        the .herring files in the temp file structure.  Finally the temp
        files are removed.
        """
        base_dir = mkdtemp()
        files = [
            'herringfile',
            'herringlib/__init__.py',
            'herringlib/f1.py',
            'herringlib/f2.py',
            'herringlib/f3.foo',
            'herringlib/f4/__init__.py',
            'herringlib/f4/herring',
            'herringlib/f4/f5.py',
            'herringlib/herring',
            'herringlib/herringfile'
        ]
        try:
            for file_ in [os.path.join(base_dir, f) for f in files]:
                dir_name = os.path.dirname(file_)
                if not os.path.isdir(dir_name):
                    os.makedirs(dir_name)
                with open(file_, 'w'):
                    pass

            expected = list([
                'herringlib/f1.py',
                'herringlib/f2.py',
                'herringlib/f4/f5.py'
            ])

            lib_path = Path(base_dir, 'herringlib')
            found = list(HerringLoader.library_files(library_paths=[lib_path]))

            self.assertEqual(sorted(found), sorted(expected))
        finally:
            shutil.rmtree(base_dir)

    def test_library_files_none(self):
        # noinspection PyArgumentEqualDefault
        self.assertEqual(len(list(HerringLoader.library_files(library_paths=None))), 0)
