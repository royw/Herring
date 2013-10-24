# coding=utf-8
"""
Add the following to your *requirements.txt* file:

* coverage
* nose

"""
from herring.herring_file import HerringFile

__docformat__ = 'restructuredtext en'

from herring.herring_app import task, run
from project_settings import Project

required_packages = [
    'coverage',
    'nose'
]

if HerringFile.packagesRequired(required_packages):
    @task()
    def test():
        """ Run the unit tests """
        run(("nosetests -vv --where=%s" % Project.testsDir).split(' '))
