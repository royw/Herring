# coding=utf-8
"""
Herring tasks for quality metrics (cheesecake, pymetrics, pycabehtml, pylint).

.. note::

    you may need to install pymetrics using your OS package management tool, on
    ubuntu 12.04, just installing using pip did not provide a runnable pymetrics script.

Add the following to your *requirements.txt* file:

* cheesecake
* matplotlib
* numpy
* pycabehtml
* pylint
* pymetrics

"""

__docformat__ = 'restructuredtext en'

packages_required = [
    'Cheesecake',
    'matplotlib',
    'numpy',
    'pycabehtml',
    'pylint',
    'PyMetrics'
]

if HerringFile.packagesRequired(packages_required):
    import os
    from herring.herring_file import HerringFile
    from herring.herring_app import task
    from herringlib.runner import system

    # pylint: disable=W0604,E0602
    global Project

    @task(depends=['cheesecake', 'lint', 'complexity'])
    def metrics():
        """ Quality metrics """


    @task()
    def cheesecake():
        """ Run the cheesecake kwalitee metric """
        cheesecake_log = os.path.join(Project.qualityDir, 'cheesecake.log')
        system("cheesecake_index --path=dist/%s-%s.tar.gz --keep-log -l %s" %
               (Project.name,
                Project.version,
                cheesecake_log))


    @task()
    def lint():
        """ Run pylint with project overrides from pylint.rc """
        options = ''
        if os.path.exists(Project.pylintrc):
            options += "--rcfile=pylint.rc"
        pylint_log = os.path.join(Project.qualityDir, 'pylint.log')
        system("pylint {options} {dir} > {log}".format(options=options, dir=Project.package, log=pylint_log))


    @task()
    def complexity():
        """ Run McCabe code complexity """
        quality_dir = Project.qualityDir
        complexity_txt = os.path.join(quality_dir, 'complexity.txt')
        graph = os.path.join(quality_dir, 'output.png')
        acc = os.path.join(quality_dir, 'complexity_acc.txt')
        metrics_html = os.path.join(quality_dir, 'complexity_metrics.html')
        system("touch %s" % complexity_txt)
        system("touch %s" % acc)
        system("pymetrics --nosql --nocsv `find %s/ -iname \"*.py\"` > %s" %
               (Project.package, complexity_txt))
        system("pycabehtml.py -i %s -o %s -a %s -g %s" %
               (complexity_txt, metrics_html, acc, graph))
