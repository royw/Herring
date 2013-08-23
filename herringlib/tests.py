# coding=utf-8
"""
Add the following to your *requirements.txt* file:

* coverage
* nose

"""

__docformat__ = 'restructuredtext en'

from herring.herring_app import task, run


# pylint: disable=W0604,E0602
global Project


@task()
def test():
    """ Run the unit tests """
    run(("nosetests -vv --where=%s" % Project.testsDir).split(' '))
