import fnmatch
import os
from herring.support.SimpleLogger import info


def recursively_remove(path, pattern):
    """ recursively remove files that match a given pattern """
    files = [os.path.join(dir_path, f)
             for dir_path, dir_names, files in os.walk(path)
             for f in fnmatch.filter(files, pattern)]
    for file_ in files:
        info("removing: %s" % file_)
        os.remove(file_)
