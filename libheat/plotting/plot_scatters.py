"""Plots the scatter plot figures which may end up in the paper."""

import matplotlib.pyplot as plt
import pandas as pd

from libheat.plotting import dream_details


def communication(df):
    tabledf = dream_details.dream_table(df)
    df0 = tabledf.loc[tabledf["sc_threshold"] == 0]
    df00625 = tabledf.loc[tabledf["sc_threshold"] == 0.0625]
    df0125 = tabledf.loc[tabledf["sc_threshold"] == 0.125]
    df025 = tabledf.loc[tabledf["sc_threshold"] == 0.25]
    df05 = tabledf.loc[tabledf["sc_threshold"] == 0.5]
    df1 = tabledf.loc[tabledf["sc_threshold"] == 1]

    plt.scatter(df0["send_freq"] / 100,
                df0["robustness"] / 100,
                marker="o",
                c=(0, 0, 0, 0.5), zorder=3,
                label="mSC = 0")
    plt.scatter(df00625["send_freq"] / 100,
                df00625["robustness"] / 100,
                marker="<",
                c=(0.05, 0.05, 0.05, 0.5), zorder=4,
                label="mSC = 0.0625")
    plt.scatter(df0125["send_freq"] / 100,
                df0125["robustness"] / 100,
                marker="*",
                c=(0.05, 0.05, 0.05, 0.5), zorder=4,
                label="mSC = 0.125")
    plt.scatter(df025["send_freq"] / 100,
                df025["robustness"] / 100,
                marker="^",
                c=(0.1, 0.1, 0.1, 0.5), zorder=5,
                label="mSC = 0.25")
    plt.scatter(df05["send_freq"] / 100,
                df05["robustness"] / 100,
                marker="h",
                c=(0.15, 0.15, 0.15, 0.5), zorder=6,
                label="mSC = 0.5")
    plt.scatter(df1["send_freq"] / 100,
                df1["robustness"] / 100,
                marker="X",
                c=(0.2, 0.2, 0.2, 0.5), zorder=6,
                label="mSC = 1")
    plt.xlabel("Communications Relative to DREA")
    plt.ylabel("Robustness Relative to DREA")
    plt.ylim(0.2, 1.08)
    plt.xlim(0.2, 1.08)
    plt.title("Overall Communications V.S. Robustness")
    plt.grid(color=(0.95, 0.95, 0.95), zorder=-1)
    plt.legend(prop={'size': 6})
    plt.tight_layout()


def reschedules(df):
    tabledf = dream_details.dream_table(df)

    df0 = tabledf.loc[tabledf["ar_threshold"] == 0]
    df00625 = tabledf.loc[tabledf["ar_threshold"] == 0.0625]
    df0125 = tabledf.loc[tabledf["ar_threshold"] == 0.125]
    df025 = tabledf.loc[tabledf["ar_threshold"] == 0.25]
    df05 = tabledf.loc[tabledf["ar_threshold"] == 0.5]
    df1 = tabledf.loc[tabledf["ar_threshold"] == 1]

    plt.scatter(df0["reschedule_freq"] / 100,
                df0["robustness"] / 100,
                marker="o",
                c=(0, 0, 0, 0.5), zorder=3,
                label="mAR = 0.0")
    plt.scatter(df00625["reschedule_freq"] / 100,
                df00625["robustness"] / 100,
                marker="<",
                c=(0, 0, 0, 0.5), zorder=3,
                label="mAR = 0.0625")
    plt.scatter(df0125["reschedule_freq"] / 100,
                df0125["robustness"] / 100,
                marker="*",
                c=(0.05, 0.05, 0.05, 0.5), zorder=4,
                label="mAR = 0.125")
    plt.scatter(df025["reschedule_freq"] / 100,
                df025["robustness"] / 100,
                marker="^",
                c=(0.1, 0.1, 0.1, 0.5), zorder=5,
                label="mAR = 0.25")
    plt.scatter(df05["reschedule_freq"] / 100,
                df05["robustness"] / 100,
                marker="h",
                c=(0.15, 0.15, 0.15, 0.5), zorder=6,
                label="mAR = 0.5")
    plt.scatter(df1["reschedule_freq"] / 100,
                df1["robustness"] / 100,
                marker="X",
                c=(0.2, 0.2, 0.2, 0.5), zorder=6,
                label="mAR = 1")
    plt.xlabel("Reschedules Relative to DREA")
    plt.ylabel("Robustness Relative to DREA")
    plt.ylim(0.2, 1.08)
    plt.xlim(0.2, 1.08)
    plt.title("Overall Reschedules V.S. Robustness")
    plt.grid(color=(0.95, 0.95, 0.95), zorder=-1)
    plt.tight_layout()
    plt.legend(prop={"size": 6}, loc="lower right", bbox_to_anchor=(0.3, 0.0))
