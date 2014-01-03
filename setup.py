# from distutils.core import setup
import os
import re
from setuptools import setup

#from sys import version
#
#if version < '2.2.3':
#    print 'herring requires python 2.6 or newer'
#    exit(-1)


VERSION_REGEX = r'__version__\s*=\s*[\'\"](\S+)[\'\"]'


def get_project_version():
    """
    Get the version from __init__.py with a line: /^__version__\s*=\s*(\S+)/
    If it doesn't exist try to load it from the VERSION.txt file.
    If still no joy, then return '0.0.0'

    :returns: the version string
    :rtype: str
    """

    # trying __init__.py first
    try:
        file_name = os.path.join(os.getcwd(), 'herring', '__init__.py')
        with open(file_name, 'r') as inFile:
            for line in inFile.readlines():
                match = re.match(VERSION_REGEX, line)
                if match:
                    return match.group(1)
    except IOError:
        pass

    # no joy, so try getting the version from a VERSION.txt file.
    try:
        file_name = os.path.join(os.getcwd(), 'herring', 'VERSION.txt')
        with open(file_name, 'r') as inFile:
            return inFile.read().strip()
    except IOError:
        pass

    # no joy again, so return default
    return '0.0.0'

# find first README.{rst|md|txt} that exists and load into long_description.
readmes = [readme for readme in [os.path.join(os.getcwd(), 'README.{ext}'.format(ext=ext))
                                 for ext in ['.rst', '.md', '.txt']] if os.path.exists(readme)]

long_description = ''
if readmes:
    long_description = open(readmes[0]).read()

setup(
    name='Herring',
    version=get_project_version(),
    author='Roy Wright',
    author_email='roy@wright.org',
    url='http://herring.example.com',
    packages=['herring', 'herring.support'],
    # package_dir={'herring': 'herring'},
    package_data={'herring': ['*.txt']},
    license='license.txt',
    description='Just a python make utility.',
    long_description=long_description,
    install_requires=[
        "argparse",
        'yolk',
        'ordereddict',
        'unipath',
        # "Foo >= 1.2.3"
    ],
    entry_points={
        'console_scripts': ['herring = herring.herring_main:main']
    },
    test_suite="tests")
