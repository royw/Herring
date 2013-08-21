# coding=utf-8
"""
Add the following to your *requirements.txt* file:

* coverage
* nose

"""

from herring.herring_app import task, run


global Project


@task()
def test():
    """ Run the unit tests """
    run(("nosetests -vv --where=%s" % Project.testsDir).split(' '))
