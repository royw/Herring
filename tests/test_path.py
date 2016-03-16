# coding=utf-8

"""
tests the Path class
"""
from herring.support.path import Path


def test_comparisons():
    set_a = set([Path('foo', 'f1'), Path('foo', 'f2'), Path('foo', 'f3', 'f4')])
    set_b = set([Path('foo', 'f1'), Path('foo', 'f2'), Path('foo', 'f3', 'f4')])

    assert sorted(set_a) == sorted(set_b)


def test_slashes():
    a_path = Path('/smsclient/jre', './foo/bar')
    assert str(a_path) == '/smsclient/jre/foo/bar'
    assert '/smsclient/jre/foo/bar' == str(a_path)
    assert a_path.is_absolute()


def test_slashes2():
    a_path = Path('/smsclient/jre', 'foo/bar')
    assert str(a_path) == '/smsclient/jre/foo/bar'
    assert a_path.is_absolute()
