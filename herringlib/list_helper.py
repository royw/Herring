# coding=utf-8
"""
Helpers for list manipulation.  Basically modelled from ruby's Array.compress, Array.uniq

Add the following to your *requirements.txt* file:

* ordereddict

"""

__docformat__ = 'restructuredtext en'

from ordereddict import OrderedDict


def compressList(src_list):
    """
    Removes None or empty items from the list

    :param src_list: source list
    :type src_list: list
    :return: compressed list
    :rtype: list
    """
    return [item for item in src_list if item]


def uniqueList(src_list):
    """
    returns a new list without any duplicates

    :param src_list: source list
    :type src_list: list
    :return: unique list
    :rtype: list
    """
    return OrderedDict.fromkeys(src_list).keys()
