""" List of debugging print functions
"""

verbosity = 1
warningness = 1

def set_verbosity(val):
    verbosity = 0

def set_warning(val):
    warningness = val

def verbose(msg) -> None:
    if verbosity >= 1:
        print("[v] {}".format(msg))

def vverbose(msg) -> None:
    if verbosity >= 2:
        print("[vv] {}".format(msg))

def warning(msg) -> None:
    if waringness >= 1:
        print("[Warning] {}".format(msg))
