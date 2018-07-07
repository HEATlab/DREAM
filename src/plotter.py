#!/usr/bin/env python3

"""
Analyses and plots the old space-separated data files.
"""

import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def main():
    args = parse_args()
    full_df = None
    for f in args.file:
        if full_df is None:
            full_df = pd.read_csv(f, header=0)
        else:
            df = pd.read_csv(f, header=0)
            full_df = full_df.append(df)
    #plot_robustness(full_df)
    plot_reschedule(full_df)


def plot_robustness(df):
    early = df.loc[df['execution'] == "early"]
    srea = df.loc[df['execution'] == "srea"]
    drea = df.loc[df['execution'] == "drea"]
    drea_alp = df.loc[df['execution'] == "drea-alp"]
    drea_si = df.loc[df['execution'] == "drea-si"]
    drea_ar = df.loc[df['execution'] == "drea-ar"]

    early_rob = early["robustness"].tolist()
    srea_rob = srea["robustness"].tolist()
    drea_rob = drea["robustness"].tolist()
    drea_alp_rob = drea_alp["robustness"].tolist()
    drea_si_rob = drea_si["robustness"].tolist()
    drea_ar_rob = drea_ar["robustness"].tolist()

    plt.boxplot((early_rob, srea_rob, drea_rob))
    #plt.bar(range(3), (early_rob.mean(), srea_rob.mean(), drea_rob.mean()))
    plt.show()


def plot_reschedule(df):
    drea = df.loc[df['execution'] == "drea"]
    drea_alp = df.loc[df['execution'] == "drea-alp"]
    drea_si = df.loc[df['execution'] == "drea-si"]
    drea_ar = df.loc[df['execution'] == "drea-ar"]

    ax = plt.axes()

    x_d = np.arange(0.0, 1.1, 0.1)
    res = drea["reschedule_freq"].median()
    y_d = [res]*len(x_d)
    ax.plot(x_d, y_d, "k--")

    thresholds = (0.0, 0.3, 0.5, 0.7, 1.0)
    # boxplot offsets
    plot_off = 0.035

    y_si = []
    y_alp = []
    for i, j in enumerate(thresholds):
        y_si = (drea_si.loc[drea_si["threshold"] == j]["reschedule_freq"]
                .tolist())
        y_si = [i for i in y_si if i > 0.0]
        y_alp = (drea_alp.loc[drea_alp["threshold"] == j]["reschedule_freq"]
                 .tolist())
        y_alp = [i for i in y_alp if i > 0.0]
        y_ar = (drea_ar.loc[drea_alp["threshold"] == j]["reschedule_freq"]
                .tolist())
        y_ar = [i for i in y_ar if i > 0.0]

        bp = ax.boxplot([y_si, y_alp, y_ar], positions=(j-plot_off, j,
                                                        j+plot_off),
                        widths=0.03)
        color_boxes(bp)

    ax.set_xlabel("Thresholds")
    ax.set_ylabel("Reschedules per STN")
    ax.set_xlim(min(thresholds)-plot_off*2, max(thresholds)+plot_off*2)
    ax.set_xticks(thresholds)
    ax.set_xticklabels(thresholds)

    plt.show()


def color_boxes(bp):
    plt.setp(bp["boxes"][0], color="red")
    plt.setp(bp["boxes"][1], color="blue")
    plt.setp(bp["boxes"][2], color="green")

    plt.setp(bp["medians"][0], color="red")
    plt.setp(bp["medians"][1], color="blue")
    plt.setp(bp["medians"][2], color="green")

    plt.setp(bp["caps"][0], color="red")
    plt.setp(bp["caps"][1], color="red")
    plt.setp(bp["caps"][2], color="blue")
    plt.setp(bp["caps"][3], color="blue")
    plt.setp(bp["caps"][4], color="green")
    plt.setp(bp["caps"][5], color="green")

    plt.setp(bp["whiskers"][0], color="red")
    plt.setp(bp["whiskers"][1], color="red")
    plt.setp(bp["whiskers"][2], color="blue")
    plt.setp(bp["whiskers"][3], color="blue")
    plt.setp(bp["whiskers"][4], color="green")
    plt.setp(bp["whiskers"][5], color="green")


def parse_args():
    """Parse arguments provided.
    """
    parser = argparse.ArgumentParser(prog='Plotter')
    parser.add_argument('file', nargs="+", type=str, help='Files to plot')
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
            execution_col = tight_frame[execution]
            count = execution_col.shape[0]
            means[execution] = (sum(execution_col)/float(count))
        mean_frame = mean_frame.append(means, ignore_index=True)
    print(mean_frame[TO_SHOW])


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
        for col in cols:
            drop = (row[col] == 0.0 and drop)
        if drop:
            to_drop.append(index)
    frame.drop(to_drop)


if __name__ == "__main__":
    main()
