# coding=utf-8

"""
Unit tests for Version class
"""

from unittest import TestCase
from herring.support.version import Version


class TestVersion(TestCase):
    """ Version Test Case """

    def setUp(self):
        """called before each test_*()"""
        self.v = [Version(vstr) for vstr in [
            '0.0.0',
            '0.0.1',
            '0.0.2',
            '0.0.9',
            '0.3.0',
            '0.3.4',
            '0.3.5',
            '0.4.0',
            '0.4.9',
            '1.0.0',
            '1.0.1',
            '1.10.0',
            '2.0.0',
            '2.0.11',
            '2.3.0',
            '10.0.0',
            '10.0.18',
            '10.22.0',
            '999.999.999'
        ]]

    def test_version_comparisons(self):
        """verify the comparison operators"""
        for index, version in enumerate(self.v[0:-1]):
            self.assertTrue(self.v[index] < self.v[index + 1])
            self.assertTrue(self.v[index + 1] > self.v[index])
            self.assertTrue(self.v[index] <= self.v[index + 1])
            self.assertTrue(self.v[index + 1] >= self.v[index])
            self.assertTrue(self.v[index] != self.v[index + 1])
            self.assertTrue(Version(str(self.v[index])) == self.v[index])
            self.assertTrue(Version(repr(self.v[index])) == self.v[index])

