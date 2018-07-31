"""Contains code to plot degree of synchrony to robustness, which is the plot
that appears both in the clinic workshop paper and Lund et al. (2017).

Author: Jordan R Abrahams
"""


import matplotlib.pyplot as plt


def plot_syncvrobust(df, errorbars=True, executions=None, thresholds=None):
    """Plot Sychronisation vs. Performance

    X axis: Degree of Synchronisation
    Y axis: Robustness (in percent)

    Error bars: Standard error extracted from the robustnesses of the STNs.
        Each STN is considered a datum.

    Args:
        df (DataFrame): DataFrame of results to be passed. Must have a
            "sync_deg" column.
        errorbars (boolean, optional): Should the plot have error bars? Default
            True
        executions (list, optional): List of strings of execution strats to
            plot. Default ["early", "srea", "drea"]
        thresholds (list, optional): List of floats of threshold values to
            plot. Default [0.0, 0.5, 1.0]
    """
    # Executions we care about.
    if executions is None:
        executions = ["early", "srea", "drea"]
    if thresholds is None:
        thresholds = [0.0, 0.5, 1.0]
    # Make use of that degree of synchrony we added in framefilters()
    x_values = sorted(df["sync_deg"].unique().tolist())
    # Store y values. Is of the format {execution: list of y values}
    data_y = {}
    # Store error bars. Is of the format {execution: list of error bars}
    data_err = {}
    # Iterate through every execution strategy we care about.
    for ex in executions:
        runs = df.loc[df["execution"] == ex]
        for x in x_values:
            run_deg = runs.loc[runs["sync_deg"] == x]
            if ex != "drea-si" and ex != "drea-ar":
                run_series = run_deg["robustness"]  # Get robustness.
                mean = run_series.mean()
                err = run_series.sem()  # Standard error bar.
                if ex in data_y:
                    data_y[ex].append(mean*100)
                    data_err[ex].append(err*100)
                else:
                    data_y[ex] = [mean*100]
                    data_err[ex] = [err*100]
            else:
                for t in thresholds:
                    thresh_series = run_deg.loc[run_deg["threshold"]
                                                == t]["robustness"]
                    mean = thresh_series.mean()
                    err = thresh_series.sem()
                    label = ex + "_" + str(t)  # Make a unique label for each
                    if label in data_y:
                        data_y[label].append(mean*100)
                        data_err[label].append(err*100)
                    else:
                        data_y[label] = [mean*100]
                        data_err[label] = [err*100]
    linestyles = ["-", "--", ":", "-."]
    for i, label in enumerate(data_y.keys()):
        if errorbars:
            plt.errorbar(x_values, data_y[label], yerr=data_err[label],
                         linewidth=1, label=label, capsize=3,
                         linestyle=linestyles[i % len(linestyles)])
        else:
            plt.plot(x_values, data_y[label], linewidth=1, label=label,
                         linestyle=linestyles[i % len(linestyles)])
    plt.ylim(0, 100)
    plt.xlim(0, 25)
    plt.legend()
    plt.ylabel("Robustness (%)")
    plt.xlabel("Degree of Synchronization (sec)")
    plt.title("Degree of Synchronization vs. Performance")
    plt.show()
