import os


class cd(object):
    """
    Change directory, execute block, restore directory:

    Usage:

        .. code-block:: python

            with cd(path):
                pass
    """

    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    # noinspection PyUnusedLocal
    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


