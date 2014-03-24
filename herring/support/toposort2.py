# coding=utf-8
"""
From: Topological Sort (Python recipe)
      http://code.activestate.com/recipes/578272-topological-sort/

* Slight formatting changes to PEP8 and spelling corrections. (Roy)

* Changed dictionary comprehensions to dictionary generators to support
    python 2.6. (Roy)
"""

import six

__docformat__ = "restructuredtext en"


# noinspection PySetFunctionToLiteral
def toposort2(data):
    """
    Dependencies are expressed as a dictionary whose keys are items
    and whose values are a set of dependent items. Output is a list of
    sets in topological order. The first set consists of items with no
    dependencies, each subsequent set consists of items that depend upon
    items in the preceding sets.

    >>> print('\\n'.join(repr(sorted(x)) for x in toposort2({
    ...     2: set([11]),
    ...     9: set([11,8]),
    ...     10: set([11,3]),
    ...     11: set([7,5]),
    ...     8: set([7,3]),
    ...     })))
    [3, 5, 7]
    [8, 11]
    [2, 9, 10]

    :param data: a dict with set values
    :return: generator returns lists of sets in topological order
    """

    # pylint: disable=W0622
    from functools import reduce

    # Ignore self dependencies.
    for key, value in data.items():
        value.discard(key)

    # Find all items that don't depend on anything.
    extra_items_in_deps = reduce(set.union,
                                 six.itervalues(data)) - set(six.iterkeys(data))

    # Add empty dependencies where needed
    # data.update({item: set() for item in extra_items_in_deps})
    # {item: word.count(item) for item in set(word)}
    # dict((item, word.count(item)) for item in set(word))
    data.update(dict((item, set()) for item in extra_items_in_deps))
    while True:
        ordered = set(item for item, dep in six.iteritems(data) if not dep)
        if not ordered:
            break
        yield ordered
        # data = {item: (dep - ordered)
        #         for item, dep in data.iteritems()
        #         if item not in ordered}
        data = dict((item, (dep - ordered))
                    for item, dep in six.iteritems(data)
                    if item not in ordered)

    error_format = "Cyclic dependencies exist among these items:\n%s"
    assert not data, error_format % '\n'.join(repr(x) for x in six.iteritems(data))


if __name__ == '__main__':
    import doctest

    doctest.testmod()
