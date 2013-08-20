"""
Helpers for list manipulation.  Basically modelled from ruby's Array.compress, Array.uniq

Add the following to your *requirements.txt* file:

* ordereddict

"""

from ordereddict import OrderedDict


def compressList(srcList):
    """
    Removes None or empty items from the list

    :param srcList: source list
    :type srcList: list
    :return: compressed list
    :rtype: list
    """
    return [item for item in srcList if item]


def uniqueList(srcList):
    """
    returns a new list without any duplicates

    :param srcList: source list
    :type srcList: list
    :return: unique list
    :rtype: list
    """
    return OrderedDict.fromkeys(srcList).keys()
