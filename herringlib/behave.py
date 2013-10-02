# coding=utf-8

"""
Helper for running the behave BDD utility.
"""
from herring.herring_app import task
from herring.herring_file import HerringFile

required_packages = [
    'behave'
]

if HerringFile.packagesRequired(required_packages):
    from herringlib.runner import script

    global Project

    @task(help='You may append behave options when invoking the features task.')
    def features():
        """Run behave features"""
        script('behave {features} {args}'.format(features=Project.features, args=' '.join(task.argv)))


