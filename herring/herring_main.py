#!/usr/bin/env python
# coding=utf-8

"""
This is the console entry point (from setup.py) for the herring application.
"""

__docformat__ = 'restructuredtext en'

from herring.herring_app import HerringApp
from herring.herring_cli import HerringCLI


def main():
    """
    This is the console entry point.
    """

    cli = HerringCLI()
    cli.execute(HerringApp())


if __name__ == '__main__':
    main()
