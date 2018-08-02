"""This file holds functions which calculates useful numbers from DREAM results
for the conference paper.

Author: Jordan R. Abrahams
"""


import pandas as pd


from .plot_utils import threshold_means


COLUMNS = ["ar_threshold", "sc_threshold", "robustness", "robustness_pm"]
"""Columns for the output DataFrame"""
ERROR_FAC = 1
"""Error bar Z-score"""

def dream_table(df, **kwargs):
    """Get DREAM/ARSC algorithm table.

    Args:
        df (DataFrame): DataFrame object to read from.
        **kwargs:
            sc_threshold (float): Holding si_value.
            ar_threshold (float): Holding ar_value.
            threshold_range (list): Threshold range to plot.
            comparison (str):

    Return:
        Returns a DataFrame with columns `ar_threshold`, `sc_threshold`,
        `robustness`, and `robustness_pm`.
    """
    # Start setup -------------------------------------------------------------
    srea = df.loc[df['execution'] == "srea"]
    drea = df.loc[df['execution'] == "drea"]

    if "threshold_range" in kwargs:
        thresholds = kwargs["threshold_range"]
    else:
        thresholds = [0.0, 0.0625, 0.125, 0.25, 0.5, 1.0]

    if "comparison" in kwargs:
        comparison = kwargs["comparison"]
    else:
        comparison = drea

    outdf = pd.DataFrame(columns=COLUMNS)
    # Check naming of arsi/arsc
    naming = "arsc"
    sc_col_name = "sc_threshold"
    if df.loc[df['execution'] == "arsc"].empty:
        naming = "arsi"
        sc_col_name = "si_threshold"

    for ar_thresh in thresholds:
        # Iterate through AR Thresholds, and then gather the mean robustnesses
        # for each SC threshold.
        arsc_cut = df.loc[(df['execution'] == naming)
                      & (df["ar_threshold"] == ar_thresh)]

        if comparison is None:
            data = threshold_means(arsc_cut, sc_col_name, thresholds,
                                   error_fac=ERROR_FAC)
        else:
            data = threshold_means(arsc_cut, sc_col_name, thresholds,
                comp_df=comparison, error_fac=ERROR_FAC)

        for i, sc_thresh in enumerate(thresholds):
            row_dict = {"ar_threshold": ar_thresh,
                        "sc_threshold": sc_thresh,
                        "robustness": data.robs[i],
                        "robustness_pm": data.robs_err[i]}
            outdf = outdf.append(row_dict, ignore_index=True, sort=True)

    print(outdf)
    print("DREA Rob: {}".format(drea["robustness"].mean()))
    print("DREA Rob +/-: {}".format(drea["robustness"].sem()))
    print("DREA Runtime: {}".format(drea["runtime"].mean()))
    print("DREA Runtime +/-: {}".format(drea["runtime"].sem()))
    print("DREA Reschedule: {}".format(drea["reschedule_freq"].mean()))
    print("DREA Reschedule +/-: {}".format(drea["reschedule_freq"].sem()))
    print("DREA Deployment: {}".format(drea["send_freq"].mean()))
    print("DREA Deployment +/-: {}".format(drea["send_freq"].sem()))
    return outdf


def dream_gain_table(df, **kwargs):
    """Get DREAM/ARSC algorithm table, but this time focusing on the gain

    Args:
        df (DataFrame): DataFrame object to read from.
        **kwargs:
            sc_threshold (float): Holding si_value.
            ar_threshold (float): Holding ar_value.
            threshold_range (list): Threshold range to plot.
            comparison (str):

    Return:
        Returns a DataFrame with columns `ar_threshold`, `sc_threshold`,
        `robustness`, and `robustness_pm`.
    """
    # Start setup -------------------------------------------------------------
    srea = df.loc[df['execution'] == "srea"]
    drea = df.loc[df['execution'] == "drea"]

    if "threshold_range" in kwargs:
        thresholds = kwargs["threshold_range"]
    else:
        thresholds = [0.0, 0.0625, 0.125, 0.25, 0.5, 1.0]

    if "comparison" in kwargs:
        comparison = kwargs["comparison"]
    else:
        comparison = drea

    dreamdf = pd.DataFrame(columns=COLUMNS)
    # Check naming of arsi/arsc
    naming = "arsc"
    sc_col_name = "sc_threshold"
    if df.loc[df['execution'] == "arsc"].empty:
        naming = "arsi"
        sc_col_name = "si_threshold"

    for ar_thresh in thresholds:
        # Iterate through AR Thresholds, and then gather the mean robustnesses
        # for each SC threshold.
        arsc_cut = df.loc[(df['execution'] == naming)
                      & (df["ar_threshold"] == ar_thresh)]
        data = threshold_means(arsc_cut, sc_col_name, thresholds,
                               error_fac=ERROR_FAC, use_percents=False)

        for i, sc_thresh in enumerate(thresholds):
            row_dict = {"ar_threshold": ar_thresh,
                        "sc_threshold": sc_thresh,
                        "robustness": data.robs[i],
                        "robustness_pm": data.robs_err[i],
                        "improv_rob": data.robs[i] - srea["robustness"].mean(),
                        "reschedule_freq": data.res[i],
                        "deployment": data.sends[i]}
            dreamdf = dreamdf.append(row_dict, ignore_index=True, sort=True)

    deployment_metric = dreamdf["improv_rob"]/dreamdf["deployment"]
    #deployment_metric.rename(index=str, columns={"0": "metric"})
    print(dreamdf["improv_rob"])
    print(dreamdf["deployment"])
    dreamdf["metric"] = deployment_metric

    pretty_print = dreamdf[["ar_threshold", "sc_threshold", "robustness",
                            "robustness_pm", "metric"]]
    print(pretty_print.sort_values(by=["metric"]))

    print("DREA Rob: {}".format(drea["robustness"].mean()))
    print("DREA Rob +/-: {}".format(drea["robustness"].sem()))
    print("DREA Runtime: {}".format(drea["runtime"].mean()))
    print("DREA Runtime +/-: {}".format(drea["runtime"].sem()))
    print("DREA Reschedule: {}".format(drea["reschedule_freq"].mean()))
    print("DREA Reschedule +/-: {}".format(drea["reschedule_freq"].sem()))
    print("DREA Deployment: {}".format(drea["send_freq"].mean()))
    print("DREA Deployment +/-: {}".format(drea["send_freq"].sem()))


def dream_best_ar(df):
    dream = df.loc[(df["execution"] == "drea-ar") & (df["si_threshold"] == 0)]
    srea = df.loc[df["execution"] == "srea"]
    thresholds = list(dream["ar_threshold"].unique())
    data = threshold_means(dream, "ar_threshold", thresholds, error_fac=1,
                           use_percents=False)
    dream_summary = pd.DataFrame(columns=["robustness",
                                          "ar_threshold",
                                          "sc_threshold",
                                          "reschedule_freq"])
    for i, ar_thresh in enumerate(thresholds):
        row = {"robustness": data.robs[i],
               "ar_threshold": ar_thresh,
               "sc_threshold": 0,
               "reschedule_freq": data.res[i]}
        dream_summary = dream_summary.append(row, ignore_index=True)

    metric = ((dream_summary["robustness"] - float(srea["robustness"].mean()))
              /dream_summary["reschedule_freq"])
    dream_summary["metric"] = metric
    print(dream_summary.sort_values(by="metric"))
    print("SREA robustness: {}".format(srea["robustness"].mean()))


def dream_best_sc(df):
    # For whatever reason, we are getting 1.0 send frequency with the older
    # data set.
    dream = df.loc[(df["execution"] == "arsi") & (df["ar_threshold"] == 1)]
    srea = df.loc[df["execution"] == "srea"]
    thresholds = list(dream["si_threshold"].unique())
    data = threshold_means(dream, "si_threshold", thresholds, error_fac=1,
                           use_percents=False)
    dream_summary = pd.DataFrame(columns=["robustness",
                                          "ar_threshold",
                                          "sc_threshold",
                                          "send_freq"])
    for i, sc_thresh in enumerate(thresholds):
        row = {"robustness": data.robs[i],
               "ar_threshold": 1.0,
               "sc_threshold": sc_thresh,
               "send_freq": data.sends[i]}
        dream_summary = dream_summary.append(row, ignore_index=True)

    metric = ((dream_summary["robustness"] - float(srea["robustness"].mean()))
              /dream_summary["send_freq"])
    dream_summary["metric"] = metric
    print(dream_summary.sort_values(by="metric"))
    print("SREA robustness: {}".format(srea["robustness"].mean()))


def dream_gain_table_q2(df, **kwargs):
    """Get DREAM/ARSC algorithm table, but this time focusing on the gain

    Args:
        df (DataFrame): DataFrame object to read from.
        **kwargs:
            sc_threshold (float): Holding si_value.
            ar_threshold (float): Holding ar_value.
            threshold_range (list): Threshold range to plot.
            comparison (str):

    Return:
        Returns a DataFrame with columns `ar_threshold`, `sc_threshold`,
        `robustness`, and `robustness_pm`.
    """
    # Start setup -------------------------------------------------------------
    srea = df.loc[df['execution'] == "srea"]
    drea = df.loc[df['execution'] == "drea"]

    if "threshold_range" in kwargs:
        thresholds = kwargs["threshold_range"]
    else:
        thresholds = [0.0, 0.0625, 0.125, 0.25, 0.5, 1.0]

    if "comparison" in kwargs:
        comparison = kwargs["comparison"]
    else:
        comparison = drea

    dreamdf = pd.DataFrame(columns=COLUMNS)
    # Check naming of arsi/arsc
    naming = "arsc"
    sc_col_name = "sc_threshold"
    if df.loc[df['execution'] == "arsc"].empty:
        naming = "arsi"
        sc_col_name = "si_threshold"

    for ar_thresh in thresholds:
        # Iterate through AR Thresholds, and then gather the mean robustnesses
        # for each SC threshold.
        arsc_cut = df.loc[(df['execution'] == naming)
                      & (df["ar_threshold"] == ar_thresh)]
        data = threshold_means(arsc_cut, sc_col_name, thresholds,
                               error_fac=ERROR_FAC, use_percents=False)

        for i, sc_thresh in enumerate(thresholds):
            row_dict = {"ar_threshold": ar_thresh,
                        "sc_threshold": sc_thresh,
                        "robustness": data.robs[i],
                        "robustness_pm": data.robs_err[i],
                        "improv_rob": data.robs[i] - srea["robustness"].mean(),
                        "reschedule_freq": data.res[i],
                        "deployment": data.sends[i],
                        "runtime": data.runtimes[i],
                        "runtime_pm": data.runtimes_err[i]}
            dreamdf = dreamdf.append(row_dict, ignore_index=True, sort=True)

    deployment_metric_2 = dreamdf["improv_rob"]/dreamdf["runtime"]
    #deployment_metric.rename(index=str, columns={"0": "metric"})
    print(dreamdf["improv_rob"])
    print(dreamdf["deployment"])
    dreamdf["metric_2"] = deployment_metric_2

    pretty_print = dreamdf[["ar_threshold", "sc_threshold", "robustness",
                            "robustness_pm",
                            "runtime",
                            "runtime_pm",
                            "metric_2"]]
    print(pretty_print.sort_values(by=["metric_2"]))

    print("DREA Rob: {}".format(drea["robustness"].mean()))
    print("DREA Rob +/-: {}".format(drea["robustness"].sem()))
    print("DREA Runtime: {}".format(drea["runtime"].mean()))
    print("DREA Runtime +/-: {}".format(drea["runtime"].sem()))
    print("DREA Reschedule: {}".format(drea["reschedule_freq"].mean()))
    print("DREA Reschedule +/-: {}".format(drea["reschedule_freq"].sem()))
    print("DREA Deployment: {}".format(drea["send_freq"].mean()))
    print("DREA Deployment +/-: {}".format(drea["send_freq"].sem()))
