# coding=utf-8

"""
tests the Path class
"""
import pytest

from herring.support.path import Path


def test_comparisons():
    set_a = set([Path('foo', 'f1'), Path('foo', 'f2'), Path('foo', 'f3', 'f4')])
    set_b = set([Path('foo', 'f1'), Path('foo', 'f2'), Path('foo', 'f3', 'f4')])

    assert sorted(set_a) == sorted(set_b)


def path_test(a_path, b_path):
    assert a_path == b_path
    assert a_path == Path(b_path)
    assert str(a_path) == b_path
    assert str(a_path) == Path(b_path)

    assert b_path == a_path
    assert b_path == str(a_path)

    assert Path(b_path) == a_path
    assert Path(b_path) == str(a_path)

    assert a_path.is_absolute()
    assert not a_path.is_relative()


def test_slashes():
    path_test(Path('/smsclient/jre', './foo/bar'), '/smsclient/jre/foo/bar')


def test_slashes2():
    path_test(Path('/smsclient/jre', 'foo/bar'), '/smsclient/jre/foo/bar')


def test_slashes3():
    path_test(Path('/smsclient/jre/jazz', '../foo/bar'), '/smsclient/jre/foo/bar')


def test_startswith():
    assert Path('foo/bar').startswith('foo')
    assert not Path('/bar/foo').startswith('foo')


def test_item():
    path = Path('/foo/bar')

    assert path[0] == '/'
    assert path[1] == 'f'
    assert path[2] == 'o'
    assert path[3] == 'o'
    assert path[4] == '/'
    assert path[5] == 'b'
    assert path[6] == 'a'
    assert path[7] == 'r'
    assert path[-1] == 'r'

    with pytest.raises(IndexError):
        # noinspection PyStatementEffect
        path[8] == '/'
