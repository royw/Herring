# coding=utf-8

"""
This tests loading a module whose contents are in multiple directories.

Real usage is to support loading herringlib from multiple locations,
ex:  ~/.herring/herringlib and ~/project/herringlib
"""
from herring.support.unionfs import unionfs

__docformat__ = 'restructuredtext en'

import os
import sys
import shutil
from pprint import pprint
from textwrap import dedent


def mkdir_p(directory_name):
    """mkdir -p"""
    try:
        os.makedirs(directory_name)
    except OSError as err:
        if err.errno != 17:
            raise
    return directory_name


def touch(filename):
    """touch filename"""
    edit(filename=filename, data=None)


def edit(filename, data=None):
    with open(filename, 'w') as edit_file:
        if data is not None:
            edit_file.write(data)


def test_unionfs():
    """
    test loading one module from two directories

    test
    + foo
      + alpha.py
    + bar
      + bravo.py

    import alpha
    import bravo
    """
    test = 'test'
    foo_dir = os.path.join(test, 'foo')
    bar_dir = os.path.join(test, 'bar')
    mount_dir = os.path.join(test, 'mount')
    foo_init = os.path.join(foo_dir, '__init__.py')
    bar_init = os.path.join(bar_dir, '__init__.py')
    alpha_file = os.path.join(foo_dir, 'alpha.py')
    bravo_file = os.path.join(bar_dir, 'bravo.py')
    mkdir_p(foo_dir)
    mkdir_p(bar_dir)
    mkdir_p(mount_dir)
    touch(foo_init)
    touch(bar_init)
    edit(alpha_file, dedent("""\
        def alpha():
            return 'alpha'
    """))
    edit(bravo_file, dedent("""\
        def bravo():
            return 'bravo'
    """))

    old_sys_path = sys.path[:]
    # make foo:bar:sys.path
    sys.path.insert(0, test)

    # # from foo.alpha import alpha
    # globals()['alpha'] = getattr(__import__('foo.alpha', globals(), locals(), ['alpha']), 'alpha')
    # # from bar.bravo import bravo
    # globals()['bravo'] = getattr(__import__('bar.bravo', globals(), locals(), ['bravo']), 'bravo')
    #
    # pprint(locals())
    # assert alpha() == 'alpha'
    # assert bravo() == 'bravo'
    #
    with unionfs(source_dirs=[foo_dir, bar_dir], mount_dir=mount_dir):
        globals()['alpha2'] = getattr(__import__('mount.alpha', globals(), locals(), ['alpha']), 'alpha')
        globals()['bravo2'] = getattr(__import__('mount.bravo', globals(), locals(), ['bravo']), 'bravo')

        pprint(locals())
        assert alpha2() == 'alpha'
        assert bravo2() == 'bravo'

    shutil.rmtree(foo_dir)
    shutil.rmtree(bar_dir)

