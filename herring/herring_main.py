#!/usr/bin/env python
# coding=utf-8

"""
This is the console entry point (from setup.py) for the herring application.
"""
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
