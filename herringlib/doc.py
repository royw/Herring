"""
Add the following to your *requirements.txt* file:

* Pygments
* Sphinx
* sphinx-bootstrap-theme
* sphinx-pyreverse
* sphinxcontrib-plantuml
* sphinxcontrib-blockdiag
* sphinxcontrib-actdiag
* sphinxcontrib-nwdiag
* sphinxcontrib-seqdiag

"""

import os
import re
from herring.herring_app import task, run, HerringFile
from herring.support.SimpleLogger import info
from herringlib.cd import cd
from herringlib.clean import clean
from herringlib.recursively_remove import recursively_remove
from herringlib.safe_edit import safeEdit

global Project


@task(depends=['clean'])
def docClean():
    """Remove documentation artifacts"""
    recursively_remove(os.path.join(Project.docsDir, '_src'), '*')
    recursively_remove(os.path.join(Project.docsDir, '_epy'), '*')
    recursively_remove(os.path.join(Project.docsDir, '_build'), '*')


def hackDocSrcFile(fileName):
    # TODO: this is way too complex - Refactor!

    # autodoc generates:
    #
    # :mod:`ArgumentServiceTest` Module
    # ---------------------------------
    #
    # .. automodule:: util.unittests.ArgumentServiceTest
    #
    # need to add package path from automodule line to module name in mod line.

    # build dict from automodule lines where key is base name, value is full name
    nameDict = {}
    with open(fileName, 'r') as inFile:
        for line in inFile.readlines():
            match = re.match(r'.. automodule:: (\S+)', line)
            if match:
                value = match.group(1)
                key = value.split('.')[-1]
                nameDict[key] = value

    moduleName = os.path.splitext(os.path.basename(fileName))[0]

    # substitute full names into mod lines with base names.
    with safeEdit(fileName) as files:
        inFile = files['in']
        outFile = files['out']

        lineLength = 0
        package = False
        for line in inFile.readlines():
            match = re.match(r':mod:`(.+)`(.*)', line)
            if match:
                key = match.group(1)
                if key in nameDict:
                    value = nameDict[key]
                    line = ''.join(":mod:`%s`%s\n" % (value, match.group(2)))
                lineLength = len(line)
                package = re.search(r':mod:.+Package', line)
            elif re.match(r'[=\-\.][=\-\.][=\-\.]+', line):
                if lineLength > 0:
                    line = "%s\n" % (line[0] * lineLength)
                    if package:
                        packageImage = "uml/packages_{name}.svg".format(name=moduleName)
                        line += "\n.. figure:: {image}\n\n    {name} Packages\n\n".format(image=packageImage,
                                                                                          name=moduleName)
                    else:
                        classesImage = "uml/classes_{name}.svg".format(name=moduleName)
                        line += "\n.. figure:: {image}\n\n    {name} Classes\n\n".format(image=classesImage,
                                                                                         name=moduleName)
            outFile.write(line)

        outFile.write("\n\n")
        title = "%s Inheritance Diagrams" % moduleName
        outFile.write("%s\n" % title)
        outFile.write('-' * len(title) + "\n\n")
        for value in sorted(nameDict.values()):
            outFile.write(".. inheritance-diagram:: %s\n" % value)
        outFile.write("\n\n")


@task(depends=['docClean'])
def apiDoc():
    """Generate API sphinx source files from code"""
    with cd(Project.docsDir):
        os.system("sphinx-apidoc -d 6 -o _src ../%s" % Project.package)

    for dirName, dirNames, fileNames in os.walk(os.path.join(Project.docsDir, '_src')):
        for fileName in fileNames:
            if fileName != 'modules.rst':
                hackDocSrcFile(os.path.join(dirName, fileName))

        # ignore dot sub-directories ('.*') (mainly for skipping .svn directories)
        for name in dirNames:
            if name.startswith('.'):
                dirNames.remove(name)


def cleanDocLog(fileName):
    """
    Removes sphinx/python 2.6 warning messages.

    Messages to remove:

    * WARNING: py:class reference target not found: object
    * WARNING: py:class reference target not found: exceptions.Exception
    * WARNING: py:class reference target not found: type
    * WARNING: py:class reference target not found: tuple
    """
    with safeEdit(fileName) as files:
        inFile = files['in']
        outFile = files['out']
        for line in inFile.readlines():
            match = re.search(r'WARNING: py:class reference target not found: (\S+)', line)
            if match:
                if match.group(1) in ['object', 'exceptions.Exception', 'type', 'tuple']:
                    continue
            outFile.write(line)


@task(depends=['apiDoc'])
def docDiagrams():
    path = os.path.join(HerringFile.directory, Project.package)
    with cd(Project.umlDir):
        for module_path in [dir_path for dir_path, dir_names, files in os.walk(path)]:
            name = os.path.basename(module_path).split(".")[0]
            cmd_line = 'PYTHONPATH="{path}" pyreverse -o svg -p {name} {module}'.format(path=Project.pythonPath,
                                                                                        name=name,
                                                                                        module=module_path)
            info(cmd_line)
            os.system(cmd_line)


@task(depends=['apiDoc', 'docDiagrams'])
def sphinxDocs():
    """Generate sphinx API documents"""
    with cd(Project.docsDir):
        os.system('PYTHONPATH=%s sphinx-build -b html -d _build/doctrees -w docs.log -a -E -n . _build/html' %
                  Project.pythonPath)
        cleanDocLog('docs.log')


@task()
def idoc():
    with cd(Project.docsDir):
        os.system('PYTHONPATH=%s sphinx-build -b html -d _build/doctrees -w docs.log -n . _build/html' %
                  Project.pythonPath)
        cleanDocLog('docs.log')


@task(depends=['apiDoc'])
def epyDocs():
    """Generate epy API documents"""
    with cd(Project.docsDir):
        cmd_args = ['epydoc', '-v', '--output', '_epy', '--graph', 'all', 'bin', 'db', 'dst', 'dut', 'lab',
                    'otto', 'pc', 'tests', 'util']
        run(cmd_args)


@task(depends=['sphinxDocs'])
def doc():
    """Generate API documents"""
    pass


@task(depends=['doc'])
def doc_post_clean():
    clean()
