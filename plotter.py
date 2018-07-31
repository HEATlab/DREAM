#!/usr/bin/env python3

"""
Analyses and plots the old space-separated data files.
"""

import argparse
import matplotlib.pyplot as plt
from matplotlib import rcParams
import pandas as pd
import numpy as np


from libheat.plotting.plot_utils import framefilters
from libheat.plotting.plot_arsc import plot_arsc_cross
from libheat.plotting.plot_ara import plot_ara
from libheat.plotting.plot_syncvrobust import plot_syncvrobust
from libheat.plotting.dream_details import dream_table


CM2INCH = 0.393701
DEFAULT_WIDTH = 16
DEFAULT_HEIGHT = 11


def main():
    # Setup -------------------------------------------------------------------
    rcParams["font.family"] = "serif"

    args = parse_args()
    full_df = None
    for f in args.file:
        if full_df is None:
            full_df = pd.read_csv(f, header=0)
        else:
            df = pd.read_csv(f, header=0)
            full_df = full_df.append(df, ignore_index=True, sort=True)

    # Filter the samples
    full_df = framefilters(full_df)

    plt.figure(figsize=(CM2INCH*DEFAULT_WIDTH, CM2INCH*DEFAULT_HEIGHT))
    ax = plt.gca()
    ax.tick_params(bottom=True, top=True, left=True, right=True)

    if args.syncvrobust:
        plot_syncvrobust(full_df, errorbars=True)
    elif args.reschedules:
        plot_threshold(full_df, "si")
    elif args.arsi_threshold:
        ax.set_title("DREAM Threshold SC Analysis (m_AR = 1)")
        plot_arsc_cross(full_df, ar_threshold=1.0, ax=ax, plot_srea=True)
        #ax.set_title("DREAM Threshold AR Analysis (m_SC = 0)")
        #plot_arsc_cross(full_df, sc_threshold=0.0, ax=ax, plot_srea=True)
    elif args.ara_threshold:
        ax.set_title("DREA-AR Alternate")
        plot_ara(full_df, ax=ax, plot_srea=True)
    elif args.table:
        dream_table(full_df)
        return
    if args.output is None:
        plt.show()
    else:
        plt.savefig(args.output)


def plot_robustness(df, plot_type="box"):
    early = df.loc[df['execution'] == "early"]
    srea = df.loc[df['execution'] == "srea"]
    drea = df.loc[df['execution'] == "drea"]
    drea_alp = df.loc[df['execution'] == "drea-alp"]
    drea_si = df.loc[df['execution'] == "drea-si"]
    drea_ar = df.loc[df['execution'] == "drea-ar"]

    early_rob = early["robustness"]
    srea_rob = srea["robustness"]
    drea_rob = drea["robustness"]
    drea_alp_rob = drea_alp["robustness"]
    drea_si_rob = drea_si["robustness"]
    drea_ar_rob = drea_ar["robustness"]

    if plot_type == "box":
        plt.boxplot((early_rob.tolist(), srea_rob.tolist(), drea_rob.tolist()))
    elif plot_type == "bar":
        plt.bar(range(3), early_rob.mean(), srea_rob.mean(), drea_rob.mean())
    elif plot_type == "line":
        thresholds = [0.0, 0.25, 0.5, 0.75, 1.0]
        # SI
        rob_means = []
        rob_sd = []
        for i in thresholds:
            i_drea_si = drea_si.loc[drea_si["threshold"] == i]
            n = sum(i_drea_si["samples"])
            p = sum(i_drea_si["samples"] * i_drea_si["robustness"])\
                    / n
            sem = (p*(1-p)/n)**0.5

            rob_means.append(p)
            rob_sd.append(sem)
        plt.errorbar(thresholds, rob_means, yerr=rob_sd, capsize=4,
                     linewidth=1)
        # ALP
        rob_means = []
        rob_sd = []
        for i in thresholds:
            i_drea_alp = drea_alp.loc[drea_si["threshold"] == i]
            n = sum(i_drea_alp["samples"])
            p = sum(i_drea_alp["samples"] * i_drea_alp["robustness"])\
                    / n
            sem = (p*(1-p)/n)**0.5

            rob_means.append(p)
            rob_sd.append(sem)
        plt.errorbar(thresholds, rob_means, yerr=rob_sd, capsize=4,
                     linewidth=1)
        # AR
        rob_means = []
        rob_sd = []
        for i in thresholds:
            i_drea_ar = drea_ar.loc[drea_si["threshold"] == i]
            n = sum(i_drea_ar["samples"])
            p = sum(i_drea_ar["samples"] * i_drea_ar["robustness"])\
                    / n
            sem = (p*(1-p)/n)**0.5

            rob_means.append(p)
            rob_sd.append(sem)
        plt.errorbar(thresholds, rob_means, yerr=rob_sd, capsize=3,
                     linewidth=0)

        plt.plot(thresholds, np.full(4, drea_rob.mean()))
        plt.plot(thresholds, np.full(5, srea_rob.mean()))
    plt.show()


def sd_v_robust(df):
    """Plot Standard Deviation of Contingent Edges vs. Performance
        Produces a scatterplot.

    X axis: Mean of the standard deviations of the edges present.
    Y axis: Robustness

    Args:
        df (DataFrame): DataFrame of results to be passed. Must have a
            "sd_avg" column.
    """
    early = df.loc[df['execution'] == "early"]
    srea = df.loc[df['execution'] == "srea"]
    drea = df.loc[df['execution'] == "drea"]

    early_rob = early["robustness"]
    srea_rob = srea["robustness"]
    drea_rob = drea["robustness"]

    plt.scatter(early["sd_avg"].tolist(), early_rob.tolist(),
                alpha=0.2,
                label="Early")
    plt.scatter(srea["sd_avg"].tolist(), srea_rob.tolist(),
                alpha=0.2,
                label="SREA")
    plt.scatter(drea["sd_avg"].tolist(), drea_rob.tolist(),
                alpha=0.2,
                label="DREA")
    plt.legend()
    plt.ylabel("Robustness")
    plt.xlabel("Standard Deviation of Contingent Edges")
    plt.title("Edge Standard Deviation vs. Performance")
    plt.show()


def plot_threshold(df, alg):
    """ Plot SI thresholds when compared against DREA.

    Args:
        df (DataFrame):
        alg (str): Algorithm to analyse using the threshold.
    """

    srea = df.loc[df['execution'] == "srea"]
    drea = df.loc[df['execution'] == "drea"]
    drea_si = df.loc[df['execution'] == "drea-si"]
    drea_ar = df.loc[df['execution'] == "drea-ar"]
    early = df.loc[df['execution'] == 'early']

    srea_rob = srea["robustness"]
    early_rob = early["robustness"]
    drea_rob = drea["robustness"]
    drea_si_rob = drea_si["robustness"]
    drea_ar_rob = drea_ar["robustness"]

    thresholds = [0.0, 0.0625, 0.125, 0.25, 0.375, 0.5, 0.75, 1.0]
    drea_res = drea["reschedule_freq"].mean()
    drea_send = drea["send_freq"].mean()
    drea_run = drea["runtime"].mean()

    if "si" in alg.split():
        rob_means = []
        rob_sd = []
        sends = []
        runs = []
        for i in thresholds:
            i_drea_si = drea_si.loc[drea_si["si_threshold"] == i]
            rob_means.append(i_drea_si["robustness"].mean()/drea_rob.mean()
                             *100)
            rob_sd.append(i_drea_si["robustness"].sem()*100)
            sends.append((i_drea_si["send_freq"].mean()/drea_send)*100)
            runs.append((i_drea_si["runtime"].mean()/drea_run)*100)
        plt.errorbar(thresholds, rob_means, yerr=rob_sd, linestyle='-',
                     capsize=4, linewidth=1,
                     label="SI Robustness")
        plt.plot(thresholds, sends, linestyle='-.', linewidth=1,
                 label="SI Sent Schedules")
        plt.plot(thresholds, runs, linestyle=':', linewidth=1,
                 label="SI Runtime")
    if "ar" in alg.split():
        rob_means = []
        rob_sd = []
        res = []
        runs = []
        for i in thresholds:
            i_drea_ar = drea_ar.loc[drea_ar["ar_threshold"] == i]
            rob_means.append(i_drea_ar["robustness"].mean()/drea_rob.mean()
                             *100)
            rob_sd.append(i_drea_ar["robustness"].sem()*100)
            res.append((i_drea_ar["reschedule_freq"].mean()/drea_res)*100)
            runs.append((i_drea_ar["runtime"].mean()/drea_run)*100)
        plt.errorbar(thresholds, rob_means, yerr=rob_sd, linestyle='-',
                     capsize=4, linewidth=1,
                     label="AR Robustness")
        plt.plot(thresholds, res, linestyle='-.', linewidth=1,
                 label="AR Reschedules")
        plt.plot(thresholds, runs, linestyle=':', linewidth=1,
                 label="AR Runtime")

    plt.plot([0.0, 1.0], [srea["robustness"].mean()/drea_rob.mean()*100]*2,
             linewidth=1, dashes=[4, 6, 2, 6],
             color="m",
             label="SREA Robustness")

    plt.ylim(0,120)
    plt.xlim(0, 1)
    plt.legend(loc="lower center")
    plt.xlabel("Threshold of Algorithm")
    plt.ylabel("Percent of DREA")
    plt.title("Trade-offs Between Communication and Performance")
    plt.show()


def clinic_ar_threshold(df):
    srea = df.loc[df['execution'] == "srea"]
    drea = df.loc[df['execution'] == "drea"]
    drea_ar = df.loc[df['execution'] == "drea-ar"]
    early = df.loc[df['execution'] == 'early']

    srea_rob = srea["robustness"]
    early_rob = early["robustness"]
    drea_rob = drea["robustness"]
    drea_ar_rob = drea_ar["robustness"]

    thresholds = [0.0, 0.25, 0.5, 0.75, 1.0]
    drea_p = sum(drea["samples"]*drea["robustness"]) / sum(drea["samples"])
    drea_res = drea["reschedule_freq"].mean()
    drea_run = drea["runtime"].mean()

    # AR
    rob_means = []
    rob_e = []
    res = []
    res_e = []
    runs = []
    runs_e = []
    for i in thresholds:
        i_drea_ar = drea_ar.loc[drea_ar["threshold"] == i]
        n = sum(i_drea_ar["samples"])
        p = sum(i_drea_ar["samples"] * i_drea_ar["robustness"])\
                / n
        sem = ((p*(1-p)/n)**0.5)*100
        rob_means.append((1-i_drea_ar["robustness"].mean()/drea_rob.mean())
                         *100)
        #rob_means.append((1 - p/drea_p)*100)
        rob_e.append(i_drea_ar["robustness"].sem()*100)
        res.append((1 - i_drea_ar["reschedule_freq"].mean()/drea_res)*100)
        res_e.append(i_drea_ar["reschedule_freq"].sem()*100)
        runs.append((1 - i_drea_ar["runtime"].mean()/drea_run)*100)
        runs_e.append(i_drea_ar["runtime"].sem()*100)

    plt.errorbar(thresholds, rob_means, yerr=rob_e, linestyle='-', capsize=3,
                 linewidth=1, label="Empirical Success Rate (%)")
    plt.plot(thresholds, res, linestyle='-.', linewidth=1,
             label="Number of Reschedules")
    plt.plot(thresholds, runs, linestyle=':', linewidth=1, label="Runtime")

    plt.ylim(-40, 100)
    plt.xlim(0, 1)
    plt.legend(loc="lower center")
    plt.xlabel("Allowable Risk Threshold")
    plt.ylabel("Percent Reduction from DREA")
    plt.title("Trade-offs Between Communication and Performance in AR")
    plt.show()


def plot_reschedule(df, plot_type="box"):
    drea = df.loc[df['execution'] == "drea"]
    drea_alp = df.loc[df['execution'] == "drea-alp"]
    drea_si = df.loc[df['execution'] == "drea-si"]
    drea_ar = df.loc[df['execution'] == "drea-ar"]

    ax = plt.axes()

    x_d = np.arange(0.0, 1.1, 0.1)
    res = drea["reschedule_freq"].median()
    y_d = [res]*len(x_d)
    ax.plot(x_d, y_d, "k--")

    thresholds = (0.0, 0.25, 0.5, 0.75, 1.0)
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
    parser.add_argument("-r", "--robustness", action="store_true")
    parser.add_argument("--syncvrobust", action="store_true")
    parser.add_argument("-s", "--reschedules", action="store_true")
    parser.add_argument("--arsi-threshold", action="store_true")
    parser.add_argument("--ara-threshold", action="store_true")
    parser.add_argument("--table", action="store_true")
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Output file name")
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


if __name__ == "__main__":
    main()
