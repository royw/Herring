# coding=utf-8

"""
Setup for Herring.
"""

import os
import re
import sys
from setuptools import setup

if sys.version_info < (2, 6):
    print('herring requires python 2.6 or newer')
    exit(-1)


VERSION_REGEX = r'__version__\s*=\s*[\'\"](\S+)[\'\"]'


# noinspection PyArgumentEqualDefault
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
        # noinspection PyBroadException
        try:
            # python3
            with open(file_name, 'r', encoding='utf-8') as inFile:
                for line in inFile.readlines():
                    match = re.match(VERSION_REGEX, line)
                    if match:
                        return match.group(1)
        except:
            # python2
            with open(file_name, 'r') as inFile:
                for line in inFile.readlines():
                    match = re.match(VERSION_REGEX, line)
                    if match:
                        return match.group(1)
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

# all versions of python
required_imports = [
    'six',
    'versio',
    'pexpect',
    'paramiko',
    'scp'
]

# libraries that have been moved into python
print("Python (%s)" % sys.version)
if sys.version_info < (3, 1):
    required_imports.extend([
        'importlib',    # new in py31
        'ordereddict',  # new in py31
        'decorator',
    ])

if sys.version_info < (2, 7, 12):
    required_imports.extend([
        "argparse",  # new in py32, backported to python 2.7.12
    ])

print("required_imports: %s" % repr(required_imports))

setup(
    # Note:  wheel python tags, ABIs, platform should be declared in setup.cfg
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
    install_requires=required_imports,
    entry_points={
        'console_scripts': ['herring = herring.herring_main:main']
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Build Tools"
    ],
    test_suite="tests")
