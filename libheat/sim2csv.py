"""
File for writing a dictionary to
"""

import os.path
import pandas as pd


def save_csv_row(row, to_file):
    """ Write dictionary to a file in CSV format.

    Args:
        row (dict): Row to write. Keys are the columns.
        to_file (str): File path to write to.
    """
    list_row = {}
    for k in row.keys():
        if not isinstance(row[k], list):
            list_row[k] = [row[k]]
        else:
            list_row[k] = row[k]

    df = pd.DataFrame.from_dict(list_row)
    to_file_abs = os.path.abspath(os.path.expanduser(to_file))
    
    if os.path.isfile(to_file_abs):
        # File exists, there should also be a header line then.
        df.to_csv(to_file_abs, index=False, header=False, mode='a',
                  encoding='utf-8')
        print("CORRECT")
    else:
        # File does not exist, make it.
        df.to_csv(to_file_abs, index=False, header=True, mode='w',
                  encoding='utf-8')
