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
