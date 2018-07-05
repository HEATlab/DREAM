""" Tool for timing functions.
Does not work if the function uses recursion.
"""

import time

func_start_times = {}
func_total_times = {}


def start(func):
    """ Start the timer for a function
    Args:
        func: String representing the name of the function.
    """
    func_start_times[func] = time.time()


def stop(func):
    time_passed = time.time() - func_start_times[func]
    if func in func_total_times:
        func_total_times[func] += time_passed
    else:
        func_total_times[func] = time_passed


def clear(func):
    func_total_times[func] = 0.0

def get_times():
    return func_total_times
