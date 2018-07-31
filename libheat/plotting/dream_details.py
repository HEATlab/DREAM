"""This file holds functions which plot ARSC results for the conference paper

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
            ax (pyplot.axes): Axes to plot on. Otherwise, plot on the default.

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

        data = threshold_means(arsc_cut, sc_col_name, thresholds,
                               drea, error_fac=ERROR_FAC)

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
