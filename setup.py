# from distutils.core import setup
import os
import re
from setuptools import setup

from sys import version

if version < '2.2.3':
    print 'herring requires python 2.6 or newer'
    exit(-1)


VERSION_REGEX = r'__version__\s*=\s*[\'\"](\S+)[\'\"]'


def getProjectVersion():
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


setup(
    name='Herring',
    version=getProjectVersion(),
    author='Roy Wright',
    author_email='roy@wright.org',
    url='http://herring.example.com',
    packages=['herring', 'herring.support', 'herring.init'],
    # package_dir={'herring': 'herring'},
    package_data={'herring': ['*.txt',
                              'init/*.template',
                              'init/herringlib/*.py',
                              'init/herringlib/templates/*.template',
                              'init/herringlib/templates/docs/*.template',
                              'init/herringlib/templates/docs/_static/*.png',
                              ]},
    license='license.txt',
    description='Just a python make utility.',
    long_description=open('README.txt').read(),
    install_requires=[
        "argparse"
        # "Foo >= 1.2.3"
    ],
    entry_points={
        'console_scripts': ['herring = herring.herring_main:main']
    })
