# coding=utf-8
from herring.init.herringlib.runner import system
from herring.support.SimpleLogger import warning

HELP = {
    'pynsource': "pyNsource generates class diagrams.  Please install from http://www.andypatterns.com/index.php/products/pynsource/",
    'pyreverse': 'pyreverse generates package and class UML diagrams and is part of pylint.  Please install pylint.'
}


def executablesAvailable(executable_list):
    for executable in executable_list:
        if not system("which {name}".format(name=executable), verbose=False).strip():
            warning(HELP[executable])
            return False
    return True
