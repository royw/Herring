# coding=utf-8

"""
Helper for populating a new project.
"""

__docformat__ = 'restructuredtext en'

import os
import shutil
import textwrap
import pkg_resources
from herring.support.simple_logger import info, error

__all__ = ('NewProject',)


class NewProject(object):
    """
    Helper for populating a new project.
    """

    def __init__(self, target_dir):
        """
        Create project infrastructure for a new project.

        :param target_dir: The top level directory for the new project
        :type target_dir: str
        """
        self.full_path = os.path.abspath(target_dir)

    def populate(self):
        """
        Populate the new project.

        If there is not a herringfile in the target directory, then create one and make
        best guesses to necessary values.

        If there is not a herringlib in the target directory, then create one and populate
        with standard development tasks.

        If there is not a package directory, then create one and populate with an package_app.py
        empty file.
        """
        self._makedirs(self.full_path)
        self.initializeHerringfile(self.full_path)
        self.initializeHerringlib(self.full_path)
        self.initializePackage(self.full_path)

    def update(self):
        """
        Updates a populated project with current herringlib tasks.

        :return:
        :rtype:
        """
        self._makedirs(self.full_path)
        self.updateHerringlib(self.full_path)

    def initializeHerringfile(self, dest_path):
        """
        Create an initial herringfile for the new project.

        :param dest_path: The directory where the herringfile goes
        :type dest_path: str
        """
        herring_file = os.path.join(dest_path, 'herringfile')
        if os.path.exists(herring_file):
            info("%s already exists!  Left unchanged." % herring_file)
            return
        name = os.path.basename(dest_path)
        package = name.lower()
        author = os.environ['USER']
        with open(herring_file, 'w') as out_file:
            template = pkg_resources.resource_string('herring.init', 'herringfile.template')
            try:
                out_file.write(template.format(name=name,
                                               package=package,
                                               author=author))
            # yes, I'm lazy and want to be sure to catch all exceptions here.
            # pylint: disable=W0703
            except Exception as ex:
                error(ex)

    def initializeHerringlib(self, dest_path):
        """
        Create an initial populated herringlib directory.

        :param dest_path:  The parent directory for the new herringlib directory.
        :type dest_path: str
        """
        herringlib_dir = os.path.join(dest_path, 'herringlib')
        if os.path.exists(herringlib_dir):
            info("%s already exists!  Left unchanged." % herringlib_dir)
            return
        lib_dir = pkg_resources.resource_filename('herring.init', 'herringlib')
        shutil.copytree(lib_dir, herringlib_dir)

    def initializePackage(self, dest_path):
        """
        Create the initial package and app file.

        :param dest_path:  The parent directory for the new package directory.
        :type dest_path: str
        """
        name = os.path.basename(dest_path)
        package_name = name.lower()
        package_dir = os.path.join(dest_path, package_name)
        if os.path.exists(package_dir):
            return
        self._makedirs(package_dir)

        init_file = os.path.join(package_dir, "__init__.py")
        open(init_file, 'w').close()

        app_file = os.path.join(package_dir, "{package}_app.py".format(package=package_name))
        with open(app_file, 'w') as out_file:
            out_file.write(textwrap.dedent("""
            def main():
                \"\"\"
                This is the console entry point

                :return: None
                \"\"\"
                pass


            if __name__ == '__main__':
                main()

            """))

    def updateHerringlib(self, dest_path):
        """
        Update a populated herringlib directory.

        :param dest_path:  The parent directory for the herringlib directory.
        :type dest_path: str
        """
        herringlib_dir = os.path.join(dest_path, 'herringlib')
        lib_dir = pkg_resources.resource_filename('herring.init', 'herringlib')
        shutil.copytree(lib_dir, herringlib_dir)

    def _makedirs(self, directory_name):
        """Safely make needed directories (mkdir -p)"""
        try:
            os.makedirs(directory_name)
        except OSError, err:
            if err.errno != 17:
                raise
        return directory_name
