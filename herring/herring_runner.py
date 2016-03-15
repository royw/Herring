# coding=utf-8

"""
Describe Me!
"""
from herring.parallelize import parallelize_process
from herring.support.list_helper import is_sequence
from herring.support.simple_logger import debug, info, error
from herring.support.toposort2 import toposort2
from herring.task_with_args import HerringTasks, TaskWithArgs

__docformat__ = 'restructuredtext en'
__author__ = 'wrighroy'


class HerringRunner(object):
    @staticmethod
    def _get_default_tasks():
        """
        Get a list of default task names (@task(default=True)).

        :return: List containing default task names.
        :rtype: list
        """
        if 'default' in HerringTasks.keys():
            return ['default']
        return []

    @staticmethod
    def _verified_tasks(task_list):
        """
        If a given task does not exist, then raise a ValueError exception.

        :return: None
        :raises ValueError:
        """
        if not task_list:
            task_list = HerringRunner._get_default_tasks()
        if not task_list:
            raise ValueError("No tasks given")
        task_names = HerringTasks.keys()
        return [name for name in task_list if name in task_names]

    @staticmethod
    def _tasks_to_depend_dict(src_tasks, herring_tasks):
        """
        Builds dictionary used by toposort2 from HerringTasks

        :param src_tasks: a List of task names
        :type src_tasks: list
        :param herring_tasks: list of tasks from the herringfile
        :type herring_tasks: dict
        :return: dict where key is task name and value is List of dependency
            task names
        :rtype: dict
        """
        data = {}
        for name in src_tasks:
            data[name] = set(herring_tasks[name]['depends'])
        return data

    @staticmethod
    def _find_dependencies(src_tasks, herring_tasks):
        """
        Finds the dependent tasks for the given source tasks, building up an
        unordered list of tasks.

        :param src_tasks: list of task names that may have dependencies
         :type src_tasks: list
        :param herring_tasks: list of tasks from the herringfile
         :type herring_tasks: dict
        :return: list of resolved (including dependencies) task names
        :rtype: list
        """
        dependencies = []
        for name in src_tasks:
            if name not in dependencies:
                dependencies.append(name)
                depend_tasks = herring_tasks[name]['depends']
                tasks = HerringRunner._find_dependencies([task_ for task_ in depend_tasks if task_ not in dependencies],
                                                         herring_tasks)
                dependencies.extend(tasks)
        return dependencies

    @staticmethod
    def _resolve_dependencies(src_tasks, herring_tasks):
        """
        Resolve the dependencies for the given list of task names.

        :param src_tasks: list of task names that may have dependencies
        :type src_tasks: list
        :param herring_tasks: list of tasks from the herringfile
        :type herring_tasks: dict
        :return: list of resolved (including dependencies) task names
        :rtype: list(list(str))
        """
        tasks = HerringRunner._find_dependencies(src_tasks, herring_tasks)
        task_lists = []
        depend_dict = HerringRunner._tasks_to_depend_dict(tasks, herring_tasks)
        for task_group in toposort2(depend_dict):
            task_lists.append(list(task_group))
        return task_lists

    @staticmethod
    def run_tasks(task_list, interactive):
        """
        Runs the tasks given on the command line.

        :param task_list: a task name or a list of task names to run
        :type task_list: str|list
        :param interactive: if asserted do not run the tasks in parallel
        :type interactive: bool
        :return: None
        """
        if not is_sequence(task_list):
            task_list = [task_list]

        verified_task_list = HerringRunner._verified_tasks(task_list)
        debug("task_list: {tasks}".format(tasks=task_list))
        debug("verified_task_list: {tasks}".format(tasks=verified_task_list))
        if not verified_task_list:
            raise ValueError('No tasks given.  Run "herring -T" to see available tasks.')
        TaskWithArgs.argv = list([arg for arg in task_list if arg not in verified_task_list])

        def task_lookup(task_name_):
            info("Running: {name} ({description})".format(name=task_name_,
                                                          description=HerringTasks[task_name_]['description']))
            TaskWithArgs.arg_prompt = HerringTasks[task_name_]['arg_prompt']
            try:
                return HerringTasks[task_name_]['task']
            except Exception as ex:
                error(str(ex))

        for task_name_list in HerringRunner._resolve_dependencies(verified_task_list, HerringTasks):
            if interactive:
                for task_name in task_name_list:
                    task_lookup(task_name)()
            else:
                parallelize_process(*[task_lookup(task_name) for task_name in task_name_list])
