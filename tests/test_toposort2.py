# coding=utf-8

"""
Unit tests for toposort2 function
"""

import pytest
from herring.support.toposort2 import toposort2


class TestToposort2:
    """ Test suite for toposort2 """
    # noinspection PySetFunctionToLiteral
    def test_toposort2(self):
        """
        Test functionality

        :return: None
        """
        data = {
            2: set([11]),
            9: set([11, 8]),
            10: set([11, 3]),
            11: set([7, 5]),
            8: set([7, 3])
        }

        expected_results = [
            [3, 5, 7],
            [8, 11],
            [2, 9, 10]
        ]

        for level in (sorted(x) for x in toposort2(data)):
            expected = expected_results.pop(0)
            assert level == expected, "level => %s, expected => %s" % (level, expected)
