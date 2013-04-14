# from distutils.core import setup
import os
from setuptools import setup

from sys import version

if version < '2.2.3':
    print 'herring requires python 2.6 or newer'
    exit(-1)


def getProjectVersion():
    """ get the version from the project's VERSION.txt file"""
    version_file = os.path.join(os.getcwd(), 'herring', 'VERSION.txt')
    with open(version_file, 'r') as f:
        return f.read().strip()


setup(
    name='Herring',
    version=getProjectVersion(),
    author='Roy Wright',
    author_email='roy@wright.org',
    url='http://herring.example.com',
    packages=['herring', 'herring.support'],
    package_dir={'': '.'},
    package_data={'herring': ['*.txt']},
    license='license.txt',
    description='Just a python make utility.',
    long_description=open('README.txt').read(),
    install_requires=[
        "argparse"
        # "Foo >= 1.2.3"
    ],
    entry_points={
        'console_scripts': ['herring = herring.herring_app:main']
    })
