#!/usr/bin/env python3

"""

Original Description:
Analyses and plots the old space-separated data files.

Comments:
The above is quite misleading, since this file has transformed significantly
from the original purpose. It's become the primary file for running any of
the present plotting code.

Author: Jordan R Abrahams
"""

import os
import argparse
import matplotlib.pyplot as plt
from matplotlib import rcParams
import pandas as pd
import numpy as np


from libheat.plotting.plot_utils import framefilters
from libheat.plotting.plot_arsc import plot_arsc_cross
from libheat.plotting.plot_ara import plot_ara
from libheat.plotting.plot_syncvrobust import plot_syncvrobust
from libheat.plotting.plot_scatters import communication as com_scatter
from libheat.plotting.plot_scatters import reschedules as res_scatter
import libheat.plotting.dream_details as dream_details


# Conversion between centimetres and US inches.
CM2INCH = 0.393701
# Default sizes in centimetres.
DEFAULT_WIDTH = 12
DEFAULT_HEIGHT = 6


def main():
    # Setup -------------------------------------------------------------------
    rcParams["font.family"] = "serif"

    args = parse_args()
    full_df = None
    files = flatten_files(args.file)
    for f in files:
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

    print(full_df["stn_path"].nunique())

    if args.syncvrobust:
        plot_syncvrobust(full_df, errorbars=True)
    elif args.reschedules:
        plot_threshold(full_df, "si")
    elif args.dream_cross_section:
        # Plot a cross section of the DREAM data.
        #ax.set_title("DREAM Threshold SC Analysis (m_AR = 1)")
        #plot_arsc_cross(full_df, ar_threshold=1.0, ax=ax, plot_srea=True,
        #                threshold_range=[0.0, 0.0625, 0.125, 0.25, 0.5, 1])
        ax.set_title("DREAM Threshold AR Analysis (m_SC = 0)")
        plot_arsc_cross(full_df, sc_threshold=0.0, ax=ax, plot_srea=True,
                        threshold_range=[0.0, 0.0625, 0.125, 0.25, 0.5, 1])
        #plot_arsc_cross(full_df, sc_threshold=0.0, ax=ax, plot_srea=True)
    elif args.ara_threshold:
        ax.set_title("DREA-AR Alternate")
        plot_ara(full_df, ax=ax, plot_srea=True)
    elif args.table:
        dream_details.dream_table(full_df)
        return
    elif args.gain_table:
        dream_details.dream_gain_table(full_df)
        return
    elif args.gain_table_q2:
        dream_details.dream_gain_table_q2(full_df)
        return
    elif args.best_ar:
        dream_details.dream_best_ar(full_df)
        return
    elif args.best_sc:
        dream_details.dream_best_sc(full_df)
        return
    elif args.com_scatter:
        com_scatter(full_df)
    elif args.res_scatter:
        res_scatter(full_df)

    if args.output is None:
        plt.show()
    else:
        plt.savefig(args.output)


def flatten_files(files):
    """Check all files in the provided list. If a directory, recurse on
        on those files.
    """
    if not isinstance(files, list):
        raise TypeError("files is instance of {}, not of type list"
                .format(type(files)))
    if len(files) == 0:
        return []
    else:
        if os.path.isdir(files[0]):
            subchildren = [ files[0] + "/" + i for i in os.listdir(files[0])]
            return flatten_files(subchildren) + flatten_files(files[1:])
        else:
            return [files[0]] + flatten_files(files[1:])


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


def parse_args():
    """Parse arguments provided.
    """
    parser = argparse.ArgumentParser(prog='Plotter')
    parser.add_argument('file', nargs="+", type=str, help='Files to plot')
    parser.add_argument("-r", "--robustness", action="store_true")
    parser.add_argument("--syncvrobust", action="store_true")
    parser.add_argument("-s", "--reschedules", action="store_true")
    parser.add_argument("--dream-cross-section", action="store_true")
    parser.add_argument("--ara-threshold", action="store_true")
    parser.add_argument("--table", action="store_true")
    parser.add_argument("--gain-table", action="store_true",
                        help="Produce a table of robustness gains over AR/SC"
                        +" thresholds. E.g. normalise over many STNs how AR/SC"
                        +" affect robustness.")
    parser.add_argument("--gain-table-q2", action="store_true",
                         help=("I can't actually remember how this differs"
                               +" from --gain-table"))
    parser.add_argument("--best-ar", action="store_true")
    parser.add_argument("--best-sc", action="store_true")
    parser.add_argument("--res-scatter", action="store_true",
                        help="Generates a reschedule rate v.s. robustness"
                            +" scatter plot, as shown in Abrahams et al.")
    parser.add_argument("--com-scatter", action="store_true",
                        help="Generates a communication rate v.s. robustness"
                            +" scatter plot, as shown in Abrahams et al.")
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Output file name")
    return parser.parse_args()


if __name__ == "__main__":
    main()
