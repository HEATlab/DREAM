#!/usr/bin/env python3

"""
Analyses and plots the old space-separated data files.
"""

import argparse
import matplotlib.pyplot as plt
import pandas as pd

DEBUG = True

INTERAGENT_TIGHTNESSES = (12000,)


EXECUTIONS = ('early',
              'stat',
              'dyn',
              'si0.0',
              'si_n_0.0',
              'suff_jchng_0.0_robustness',
              'suff_jchng_n_0.0_robustness',
              )

TO_SHOW = ['tght',
           'early',
           'stat',
           'dyn',
           'dync',
           'si0.0',
           #'si_n_0.15',
           #'si_n_0.25']
           'suff_jchng_0.0_robustness',
           'suff_jchng_0.0_count',
           'suff_jchng_n_0.0_robustness']


def main():
    args = parse_args()
    frame = pd.read_csv(args.file, delim_whitespace=True, header=0)
    print(frame[TO_SHOW])
    #analyze_data_tightness(frame, EXECUTIONS, EXECUTIONS,
    #                       INTERAGENT_TIGHTNESSES)

def parse_args():
    """Parse arguments provided.
    """
    parser = argparse.ArgumentParser(prog='Plotter')
    parser.add_argument('file', type=str, help='File to plot')
    return parser.parse_args()


def analyze_data_tightness(frame, columns, executions, interagent_tightnesses):
    """
        Retrieve a frame of the means for each of the provided execution
        strategies along interagent tightness.

        Args:
            frame: DataFrame object of the data.
            columns: Tuple of strings holding the columns we want to
                     find the means of.
            executions: Tuple of 
            interagent_tightnesses: Tuple of integers of tightnesses.
    """    
    mean_frame = pd.DataFrame(columns=['tght']+list(columns))
    for tght in interagent_tightnesses:
        tight_frame = frame.loc[frame['tght'] == tght]
        # Remove complete failure rows.
        tight_frame = remove_empty(tight_frame, executions)     
        means = {'tght': tght}
        for execution in columns:
            try:
                execution_col = tight_frame[execution]
                count = execution_col.shape[0]
                means[execution] = (sum(execution_col)/float(count))
            except KeyError as e:
                if DEBUG:
                    print("[Error] KeyError: {}".format(e))
                    continue
            except ZeroDivisionError as e:
                if DEBUG:
                    print("[Error] ZeroDivisionError at {}".format(execution))
                    continue
        mean_frame = mean_frame.append(means, ignore_index=True)
    print(mean_frame[TO_SHOW])


def remove_empty(frame, cols):
    """Remove rows which have all zeros in the provided columns"""
    to_drop = []
    for index, row in frame.iterrows():
        drop = True
        try:
            for col in cols:
                drop = (row[col] == 0.0 and drop)
            if drop:
                to_drop.append(index)
        except KeyError as e:
            if DEBUG:
                print("[Error] KeyError: {}".format(e))
    return frame.drop(to_drop)


if __name__ == "__main__":
    main()
