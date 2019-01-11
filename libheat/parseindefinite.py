"""
Author: Jordan R Abrahams (jabrahams@hmc.edu)
Last Updated: 11 January 2018

Parse the indefinite string argument command.
These are of the format [(AR,SC), (AR,SC), (AR,SC)]
"""
from .montsim import Simulator


ERR_MSG = "Argument for indefinite not [(AR,SC), ...] format"


def parse_ind_arg(s: str) -> list:
    """Parse an indefinite string argument (passed in by a user)

    Args:
        s (str): The argument to parse. Of the format [(AR,SC), ...]

    Returns:
        A list of tuples, representing the arguments.
    """
    stripped_s = s.strip()
    if stripped_s[0] != "[" or stripped_s[-1] != "]":
        raise ValueError(ERR_MSG)
    
    pairs = []
    arguments_in_waiting = []
    in_pair = False
    argument_start = -1
    argument_end = -1
    for i in range(1, len(stripped_s)-1):
        c = stripped_s[i]
        if c == "(":
            if in_pair:
                raise ValueError(ERR_MSG)
            in_pair = True
            argument_start = i + 1
        elif c == ")":
            if not in_pair:
                raise ValueError(ERR_MSG)
            in_pair = False
            argument_end = i
            arguments_in_waiting.append(
                    float(stripped_s[argument_start:argument_end]))
            pairs.append(tuple(arguments_in_waiting))
            arguments_in_waiting = []
        elif in_pair:
            if c == ",":
                argument_end = i
                arguments_in_waiting.append(
                        float(stripped_s[argument_start:argument_end]))
                argument_start = i + 1
    return pairs

