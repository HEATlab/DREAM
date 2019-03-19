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
                try:
                    synchrony = float(foldername.split("_")[4][1:])*0.001
                except IndexError:
                    synchrony = "NaN"
                sync_column.append(synchrony)
            df = df.assign(sync_deg=pd.Series(sync_column))
        # Remove zeros present in the data.
    df = clearzero(df)
    return df[df.samples >= 50]


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


def threshold_means(df, thresh_name, thresholds, comp_df=None, error_fac=1.0,
                    use_percents=True):
    """Computes the means (and standard deviations) along a set of threshold
        values. This is handy for doing the Threshold v.s. Robustness plots
        when in comparison to DREA.

    Args:
        df (DataFrame): DataFrame of the data we want to plot. Often, this
            needs to be filtered to be only one algorithm.
        thresh_name (str): String representing the column name for thresholds
        comp_df (DataFrame, optional): Data frame to compare to, percent wise.
        error_fac (float, optional): Multiply error sizes by this number.
            Particularly useful if we want to use confidence intervals. Default
            is 1.0.
        use_percents (float, optional): Return results in percents.

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
    if comp_df is not None:
        comp_rob = comp_df["robustness"].mean()
        comp_res = comp_df["reschedule_freq"].mean()
        comp_run = comp_df["runtime"].mean()
        comp_send = comp_df["send_freq"].mean()
    else:
        comp_rob = 1.0
        comp_res = 1.0
        comp_run = 1.0
        comp_send = 1.0

    rob_means = []
    stderrs = []
    sends = []
    sends_err = []
    reschedules = []
    reschedules_err = []
    runtimes = []
    runtimes_err = []

    if use_percents:
        p = 100
    else:
        p = 1

    for t in thresholds:
        point = df.loc[df[thresh_name] == t]
        mean = point["robustness"].mean()/comp_rob * p
        rob_means.append(mean)
        se = point["robustness"].sem() * p
        stderrs.append(se*error_fac)
        send_dat = point["send_freq"].mean()/comp_send * p
        sends.append(send_dat)
        send_err = point["send_freq"].sem() * p
        sends_err.append(send_err*error_fac)
        res = point["reschedule_freq"].mean()/comp_res * p
        reschedules.append(res)
        res_err = point["reschedule_freq"].sem() * p
        reschedules_err.append(res_err*error_fac)
        runtime = point["runtime"].mean()/comp_run * p
        runtimes.append(runtime)
        runtime_err = point["runtime"].sem() * p
        runtimes_err.append(runtime_err*error_fac)

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
            self.runtimes_err = runtimes_err

    return ThreshResponse(rob_means, stderrs, sends, sends_err, reschedules,
                          reschedules_err, runtimes)

def find_thresholds(df: pd.DataFrame, threshold_name: str):
    """Finds the set values of thresholds in the DataFrame

    Args:
        df: Frame to read.
        threshold_name: Name of the threshold to get the values of.

    Returns:
        An numpy array of threshold values of that threshold_name.
    """
    thresh_series = df[threshold_name]
    return thresh_series.unique()

