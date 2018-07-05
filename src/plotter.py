#!/usr/bin/env python3

"""
Analyses and plots the old space-separated data files.
"""

import argparse
import matplotlib.pyplot as plt
import pandas as pd

DEBUG = True

#INTERAGENT_TIGHTNESSES = (12000,)


#EXECUTIONS = ('early',
#              'stat',
#              'dyn',
#              'si0.0',
#              'si_n_0.0',
#              'suff_jchng_0.0_robustness',
#              'suff_jchng_n_0.0_robustness',
#              )
#
#TO_SHOW = ['tght',
#           'early',
#           'stat',
#           'dyn',
#           'dync',
#           'si0.0',
#           #'si_n_0.15',
#           #'si_n_0.25']
#           'suff_jchng_0.0_robustness',
#           'suff_jchng_0.0_count',
#           'suff_jchng_n_0.0_robustness']


def main():
    args = parse_args()
    df = pd.read_csv(args.file, header=0)
    plot_points(df)

def plot_points(df):

    early = df.loc[df['execution'] == "early"]
    srea = df.loc[df['execution'] == "srea"]
    drea = df.loc[df['execution'] == "drea"]
    drea_alp = df.loc[df['execution'] == "drea-alp"]

    # Plot early execution
    x = early["synchronous_density"].tolist()
    y = early["robustness"].tolist()
    plt.scatter(x, y, c='b', marker='.', alpha=0.4)

    # Plot srea
    x = srea["synchronous_density"].tolist()
    y = srea["robustness"].tolist()
    plt.scatter(x, y, c='r', marker='.', alpha=0.4)

    # Plot drea
    x = drea["synchronous_density"].tolist()
    y = drea["robustness"].tolist()
    plt.scatter(x, y, c='g', marker='.', alpha=0.4)

    plt.xlabel("Interagent Constraint Density")
    plt.ylabel("Robustness")

    plt.show()

def parse_args():
    """Parse arguments provided.
    """
    parser = argparse.ArgumentParser(prog='Plotter')
    parser.add_argument('file', type=str, help='File to plot')
    return parser.parse_args()


def analyze_data_tightness(frame, columns, executions, interagent_tightnesses):
    """Retrieve a frame of the means

    Args:
        frame (DataFrame): Frame object of the data.
        columns (tuple): Tuple of strings holding the columns we want to
            find the means of.
        executions (tuple): Which execution strategies to look at?
        interagent_tightnesses (tuple): Integers of tightnesses.
    """
    mean_frame = pd.DataFrame(columns=['tght']+list(columns))
    for tght in interagent_tightnesses:

        tight_frame = frame.loc[frame['tght'] == tght]
        # Remove complete failure rows.
        remove_zeroed(tight_frame, executions)

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

def group_executions(frame, columns, executions):
    """Retrieve a frame of the means

    Args:
        frame (DataFrame): Frame object of the data.
        columns (tuple): Tuple of strings holding the columns we want to
            find the means of.
        executions (tuple): Which execution strategies to look at?
        interagent_tightnesses (tuple): Integers of tightnesses.
    """

    mean_frame = pd.DataFrame(columns=['execution', 'mean_reschedule_freq',
                                       'mean_runtime', 'mean_samples'])


def remove_zeroed(frame, cols) -> None:
    """Remove rows which have all zeros in the provided columns

    Args:
        frame (DataFrame): Frame to clean from
        cols (tuple): Strings to check for zeros in simultaneously.

    Post:
        Modifies the frame in-place. Note it's a pass-by-reference.
    """
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
                pr.warning("KeyError: " + str(e))
    frame.drop(to_drop)


if __name__ == "__main__":
    main()
