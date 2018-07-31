"""This file contains debugging logging functions.

By default:

* verbosity is set to 0 (no verbose printing)
* warningness is set to 1 (standard warning printing)

The same verbosity level is used throughout all programs which import the
printer.

Logging is an important part of a full program. This is a very lightweight
module intended to be easy to use for new lab members.
"""


_verbosity = 0
_warningness = 1


def set_verbosity(val):
    """Sets the verbosity of the entire program"""
    global _verbosity
    _verbosity = val


def get_verbosity() -> int:
    """Gets the verbosity level of the entire program"""
    return _verbosity


def set_warningness(val):
    """Sets the warning level of the entire program"""
    global _warningness
    _warningness = val


def get_warningness() -> int:
    """Gets the warning level of the entire program"""
    return _warningness


def verbose(msg) -> None:
    """Print the provided message if verbosity is >= 1"""
    if _verbosity >= 1:
        print("[v] {}".format(msg))


def vverbose(msg) -> None:
    """Print the provided message if verbosity is >= 2"""
    if _verbosity >= 2:
        print("[vv] {}".format(msg))


def warning(msg) -> None:
    """Print the provided message if warning level is >= 1"""
    if _warningness >= 1:
        print("[!Warning!]  {}".format(msg))
