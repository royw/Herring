# coding=utf-8

"""
Simple touch utility.
"""


def touch(filename):
    """
    touch filename

    :param filename: file spec to touch
    :type filename: str
    """
    with open(filename, 'a'):
        pass
