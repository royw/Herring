# coding=utf-8

"""
Unit tests for AppVersion class
"""

from unittest import TestCase
from herring.support.appVersion import AppVersion


class TestVersion(TestCase):
    """ AppVersion Test Case """

    def setUp(self):
        """called before each test_*()"""
        self.v = [AppVersion(vstr) for vstr in [
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
            self.assertTrue(AppVersion(str(self.v[index])) == self.v[index])
            self.assertTrue(AppVersion(repr(self.v[index])) == self.v[index])

