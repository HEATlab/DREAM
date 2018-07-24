"""This file provides common utilities for plotting stats about the
    algorithms.
"""


import pandas as pd


def framefilters(df, add_sync_degree=True):
    """Filter a DataFrame of rows that we don't want in the first place.
    This includes things like STNs which have 0% robustness.

    This function also adds an additional column to the data set, the
    "sync_deg" column, which is used to to plot the "crucial" graphs of
    synchronous degree.

    Args:
        df (DataFrame): DataFrame to filter.
        add_sync_degree (bool, optional): Add the synchrinisation column to the
            data frame. Default is True.

    Returns:
        Returns a new DataFrame with the rows we wish to ignore removed, and
        any columns we wish to add.
    """
    if add_sync_degree:
        # Add the synchrony column, extracted from the file name.
        sync_column = []
        for i, row in df.iterrows():
            foldername = row["stn_path"].split("/")[-2]
            synchrony = float(foldername.split("_")[4][1:])*0.001
            sync_column.append(synchrony)
        df = df.assign(sync_deg=pd.Series(sync_column))
        # Remove zeros present in the data.
    df = clearzero(df)
    return df[df.samples >= 100]


def clearzero(df):
    """Remove STN rows which have 0% robustness across all runs."""
    unique_stns = df.drop_duplicates(subset="stn_path")
    to_remove = []
    for _, row in unique_stns.iterrows():
        stn_path = row["stn_path"]
        runs = df.loc[df["stn_path"] == stn_path]
        all_zero = True
        for _, run in runs.iterrows():
            if not all_zero:
                break
            all_zero = run["robustness"] <= 0.0
        if all_zero:
            to_remove.append(stn_path)
    for path in to_remove:
        indices = df.loc[df["stn_path"] == path]
        common = df.merge(indices, on=['stn_path'])
        df = df[~df.stn_path.isin(common.stn_path)]
    return df


def threshold_means(df, thresh_name, thresholds, comp_df, error_fac=1.0):
    """Computes the means (and standard deviations) along a set of threshold
        values. This is handy for doing the Threshold v.s. Robustness plots
        when in comparison to DREA.

    Args:
        df (DataFrame): DataFrame of the data we want to plot. Often, this
            needs to be filtered to be only one algorithm.
        thresh_name (str): String representing the column name for thresholds
        comp_df (DataFrame): Data frame to compare to, percent wise.
        error_fac (float, optional): Multiply error sizes by this number.
            Particularly useful if we want to use confidence intervals. Default
            is 1.0.

    Returns:
        Returns an object with properties:
            robs -> returns a list of robustness means
            robs_err -> returns list of robustness errors.
            sends -> returns a list of send frequencies.
            sends_err -> returns a list of errors of send frequencies.
            res -> returns a list of reschedule frequencies
            res_err -> returns a list of reschedule frequencies errors
            runtimes -> returns a list of runtimes.
    """
    comp_rob = comp_df["robustness"].mean()
    comp_res = comp_df["reschedule_freq"].mean()
    comp_run = comp_df["runtime"].mean()
    comp_send = comp_df["send_freq"].mean()

    rob_means = []
    stderrs = []
    sends = []
    sends_err = []
    reschedules = []
    reschedules_err = []
    runtimes = []

    for t in thresholds:
        point = df.loc[df[thresh_name] == t]
        mean = point["robustness"].mean()/comp_rob.mean() * 100
        rob_means.append(mean)
        se = point["robustness"].sem() * 100
        stderrs.append(se*error_fac)
        send_dat = point["send_freq"].mean()/comp_send * 100
        sends.append(send_dat)
        send_err = point["send_freq"].sem() * 100
        sends_err.append(send_err*error_fac)
        res = point["reschedule_freq"].mean()/comp_res * 100
        reschedules.append(res)
        res_err = point["reschedule_freq"].sem() * 100
        reschedules_err.append(res_err*error_fac)
        runtime = point["runtime"].mean()/comp_run * 100
        runtimes.append(runtime)

    class ThreshResponse(object):
        def __init__(self, robs, robs_err, sends, sends_err, res, res_err,
                     runtimes):
            self.robs = robs
            self.robs_err = robs_err
            self.sends = sends
            self.sends_err = sends_err
            self.res = res
            self.res_err = res_err
            self.runtimes = runtimes

    return ThreshResponse(rob_means, stderrs, sends, sends_err, reschedules,
                          reschedules_err, runtimes)
