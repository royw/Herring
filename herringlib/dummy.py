# coding=utf-8

"""
dummy tasks for verifying herringlib directory unions
"""

from herring.herring_app import task


@task()
def dummy():
    """this is a dummy task"""
    print("This task does nothing!")
