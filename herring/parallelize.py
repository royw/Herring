# coding=utf-8

"""
parallelize
===========

Helper function for executing a set of functions in parallel.

The functions take no input and the only output is the integer exit code (0 or positive integer).

Usage
-----

Wrap any calls that take parameters or return other than positive integer exit codes in a helper function:

::

    def alpha():
        try:
            something(with, parameters)
        except Exception as ex
            ReportService.report(IReport.ERROR, IReport.MINOR, str(ex))
            return 1
        return 0

    def beta():
        if another_thing(with, stuff)
            return 0
        return 1

then to run them in parallel::

    errors = parallelize_process(alpha, beta)

"""
import multiprocessing
import threading

import sys

try:
    # noinspection PyPep8Naming
    import Queue as queue
except ImportError:
    # noinspection PyUnresolvedReferences
    import queue as queue


try:
    # python2
    # noinspection PyCompatibility
    from StringIO import StringIO
except ImportError:
    # python3
    from io import StringIO

from herring.support.simple_logger import Logger, error, debug

__docformat__ = 'restructuredtext en'


def parallelize_process(*functions):
    """
    Run each given function as a process in parallel.

    Each function is y = f() where y is a positive integer and f() takes no arguments.

    :param functions: functions to run in parallel
    :type functions: list(function)
    :return: list of any error strings
    :rtype: list(str)
    """
    errors = []
    jobs = []
    queues = []
    previous_stdout = sys.stdout
    previous_stderr = sys.stderr

    def wrapper(function_, queue__):
        """
        Wraps the function to capture the ReportService logging which is returned via the queue.

        If the function raises an exception, return 1

        :param function_: function to execute
        :type function_: function
        :param queue__: queue used to return a string containing the ReportService log filled by the function
        :type queue__: multiprocessing.Queue
        :return: exit the processes
        :rtype: zero to indicate pass or positive integer to indicate error
        """
        # print("wrapper({name})".format(name=function.__name__))
        sys.stdout = sys.stderr = StringIO()

        try:
            debug("Starting process wrapped function")
            result = function_()
            debug("Finished process wrapped function")
        except Exception as ex:
            error("parallelize_process error: " + str(ex))
            result = 1

        messages = sys.stdout.getvalue() or ""
        debug("messages: " + messages)
        queue__.put(messages)

        # HACK: documentation says to use sys.exit() but that blows on python 2.6,
        # so using return which works on python 2.6, 2.7, 3.4
        return result

    try:
        for function in functions:
            queue_ = multiprocessing.Queue()
            queues.append(queue_)
            process = multiprocessing.Process(name=function.__name__, target=wrapper, args=(function, queue_,))
            jobs.append(process)
            process.start()

        for job in jobs:
            queue_ = queues.pop(0)
            value = queue_.get()
            if value is not None and value:
                previous_stdout.write("process: " + value)
            job.join()
            if job.exitcode is None:
                errors.append("job {name} has not yet terminated".format(name=job.name))
            elif job.exitcode > 0:
                errors.append("job {name} exited with {code}".format(name=job.name, code=job.exitcode))
            elif job.exitcode < 0:
                errors.append("job {name} terminated by signal {code}".format(name=job.name, code=job.exitcode))
    finally:
        previous_stdout.flush()
        previous_stderr.flush()
        sys.stdout.flush()
        sys.stderr.flush()
        sys.stdout = previous_stdout
        sys.stderr = previous_stderr
        for error_msg in errors:
            error("process error: " + error_msg)

    return errors


def parallelize_thread(*functions):
    errors = []
    jobs = []
    queues = []

    previous_stdout = Logger.out_stream
    previous_stderr = Logger.err_stream
    thread_local = threading.local()

    class ThreadOut(object):
        def __getattr__(self, item):
            thread_io = getattr(thread_local, 'thread_io', previous_stdout)
            return getattr(thread_io, item, None)

    Logger.out_stream = Logger.err_stream = lambda: ThreadOut()

    def wrapper(function_, queue__):
        """
        Wraps the function to capture the ReportService logging which is returned via the queue.

        If the function raises an exception, return 1

        :param function_: function to execute
        :type function_: function
        :param queue__: queue used to return a string containing the ReportService log filled by the function
        :type queue__: multiprocessing.Queue
        :return: exit the processes
        :rtype: zero to indicate pass or positive integer to indicate error
        """
        # print("wrapper({name})".format(name=function.__name__))
        thread_local.thread_io = StringIO()

        try:
            exitcode_ = function_()
        except Exception as ex:
            error(str(ex))
            exitcode_ = 1

        queue__.put((exitcode_, thread_local.thread_io.getvalue()))

    try:
        for function in functions:
            queue_ = queue.Queue()
            queues.append(queue_)
            process = threading.Thread(name=function.__name__, target=wrapper, args=(function, queue_,))
            jobs.append(process)
            process.start()

        for job in jobs:
            queue_ = queues.pop(0)
            exitcode, value = queue_.get()
            # noinspection PyUnresolvedReferences
            previous_stdout.write(value)
            job.join()
            if exitcode is None:
                errors.append("job {name} has not yet terminated".format(name=job.name))
            elif exitcode > 0:
                errors.append("job {name} exited with {code}".format(name=job.name, code=exitcode))
            elif exitcode < 0:
                errors.append("job {name} terminated by signal {code}".format(name=job.name, code=exitcode))
    finally:
        # noinspection PyUnresolvedReferences
        previous_stdout.flush()
        Logger.out_stream = previous_stdout
        Logger.err_stream = previous_stderr
        for error_msg in errors:
            error(error_msg)

    return errors
