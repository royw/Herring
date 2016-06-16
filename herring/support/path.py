# coding=utf-8

"""
Python 2/3 portable subset of pathlib.
"""

import os


# noinspection PyDocstring
class Path(object):

    def __init__(self, *path_parts):
        self.__path = os.path.normpath(os.path.join(*[str(part) for part in path_parts]))
        self.name = os.path.basename(self.__path)
        self.parent = os.path.dirname(self.__path)
        self.stem = os.path.splitext(self.name)[0]

    def is_absolute(self):
        return os.path.isabs(self.__path)

    def is_relative(self):
        return not self.is_absolute()

    def relative_to(self, parent_path):
        return os.path.relpath(self.__path, parent_path)

    def is_dir(self):
        return os.path.isdir(self.__path)

    def __str__(self):
        return self.__path

    def __repr__(self):
        return repr(self.__path)

    def __hash__(self):
        return self.__path.__hash__()

    def _cmpkey(self):
        return self.__path

    def _compare(self, other, method):
        try:
            # noinspection PyProtectedMember
            return method(self._cmpkey(), Path(str(other))._cmpkey())
        except (AttributeError, TypeError):
            # _cmpkey not implemented, or return different type,
            # so I can't compare with "other".
            return NotImplemented

    def __lt__(self, other):
        return self._compare(other, lambda s, o: s < o)

    def __le__(self, other):
        return self._compare(other, lambda s, o: s <= o)

    def __eq__(self, other):
        return self._compare(other, lambda s, o: s == o)

    def __ge__(self, other):
        return self._compare(other, lambda s, o: s >= o)

    def __gt__(self, other):
        return self._compare(other, lambda s, o: s > o)

    def __ne__(self, other):
        return self._compare(other, lambda s, o: s != o)

    def __getattr__(self, item):
        """
        method not found so delegate to the private string __path attribute
        """
        return getattr(self.__path, item)

    def __getitem__(self, item):
        """
        method delegates item accessing to private string __path attribute
        """
        return self.__path[item]
