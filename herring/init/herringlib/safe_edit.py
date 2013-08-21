# coding=utf-8

"""
Safely edit a file by creating a backup which will be restored on any error.
"""
from contextlib import contextmanager
import os
import shutil
from tempfile import NamedTemporaryFile


# noinspection PyBroadException
@contextmanager
def safeEdit(fileName):
    """
    Edit a file using a backup.  On any exception, restore the backup.

    Usage::

        with safeEdit(fileName) as files:
            for line in files['in'].readlines():
                # edit line
                files['out'].write(line)

    :param fileName:  source file to edit
    :type fileName: str
    :yield: dict containing open file instances for input (files['in']) and output (files['out'])
    :raises: allows IO exceptions to propagate
    """
    backupName = fileName + '~'

    inFile = None
    tfName = None
    tf = None
    try:
        inFile = open(fileName, 'r')
        tf = NamedTemporaryFile(delete=False)
        tfName = tf.name
        yield {'in': inFile, 'out': tf}
    except:
        # on any exception, delete the output temporary file
        tf.close()
        os.remove(tfName)
        tf = None
        tfName = None
        raise
    finally:
        if inFile:
            inFile.close()
        if tf:
            tf.close()
        if tfName:
            # ideally this block would be thread locked at os level
            # remove previous backup file if it exists
            try:
                os.remove(backupName)
            except:
                pass

            # Note, shutil.move will safely move even across file systems

            # backup source file
            shutil.move(fileName, backupName)

            # put new file in place
            shutil.move(tfName, fileName)
