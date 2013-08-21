# coding=utf-8
"""
Brute force class for allowing sorting of found versions by implementing
comparisons.

Limitations:
only supports three part integer versions of the form:
major.minor.patch
where major, minor, and patch are integers.


Usage:
>>> v1 = AppVersion('1.2.3')
>>> v2 = AppVersion('1.25.4')
>>> v3 = AppVersion('1.3.1')
>>> v1 < v2
True
>>> v1 < v3
True
>>> v3 <= v2
True
>>> str(v3)
'1.3.1'
>>> repr(v2)
'1.25.4'
"""
__docformat__ = "restructuredtext en"

__all__ = ('AppVersion',)


class AppVersion(object):
    """
    Provide version comparisons for A.B.C style version strings.
    """
    def __init__(self, version_str):
        """
        The version_str must be of the form A.B.C where A, B, and C are
        integers.
        """
        self.major, self.minor, self.patch = map(int, version_str.split('.'))

    def __lt__(self, other):
        """ less than """
        if self.major < other.major:
            return True
        if self.major > other.major:
            return False

        # majors are equal
        if self.minor < other.minor:
            return True
        if self.minor > other.minor:
            return False

        # minors are equal
        return self.patch < other.patch

    def __le__(self, other):
        """ less than or equal """
        if self.major < other.major:
            return True
        if self.major > other.major:
            return False

        # majors are equal
        if self.minor < other.minor:
            return True
        if self.minor > other.minor:
            return False

        # minors are equal
        return self.patch <= other.patch

    def __gt__(self, other):
        """ greater than """
        if self.major > other.major:
            return True
        if self.major < other.major:
            return False

        # majors are equal
        if self.minor > other.minor:
            return True
        if self.minor < other.minor:
            return False

        # minors are equal
        return self.patch > other.patch

    def __ge__(self, other):
        """ greater than or equals """
        if self.major > other.major:
            return True
        if self.major < other.major:
            return False

        # majors are equal
        if self.minor > other.minor:
            return True
        if self.minor < other.minor:
            return False

        # minors are equal
        return self.patch >= other.patch

    def __eq__(self, other):
        """ equals """
        return(self.major == other.major and
               self.minor == other.minor and
               self.patch == other.patch)

    def __ne__(self, other):
        """ not equals """
        return(self.major != other.major or
               self.minor != other.minor or
               self.patch != other.patch)

    def __str__(self):
        """ String representation """
        return "%d.%d.%d" % (self.major, self.minor, self.patch)

    def __repr__(self):
        """ String representation """
        return "%d.%d.%d" % (self.major, self.minor, self.patch)
