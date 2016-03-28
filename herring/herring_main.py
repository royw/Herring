#!/usr/bin/env python
# coding=utf-8

"""
This is the console entry point (from setup.py) for the herring application.
"""

# hack the system path so you can run this file directly in your dev environment and it also works fine packaged.
# note that importing hack_sys_path will modify the system path so should be the first import in your "main" module.
# noinspection PyUnresolvedReferences
import hack_sys_path

from herring.herring_app import HerringApp
from herring.herring_cli import HerringCLI

__docformat__ = 'restructuredtext en'


def main():
    """
    This is the console entry point.
    """

    cli = HerringCLI()
    cli.execute(HerringApp())


if __name__ == '__main__':
    main()
