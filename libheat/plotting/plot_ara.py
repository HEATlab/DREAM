

import matplotlib.pyplot as plt


from .plot_utils import threshold_means


X_AXIS_RANGE = (-0.02, 1.02)
Y_AXIS_RANGE = (-10, 120)
ERROR_FAC = 1.96


def plot_ara(df, **kwargs):
    """ Plot ARA algorithm threshold
    Args:
        df (DataFrame): DataFrame object to read from.
        **kwargs:
            threshold_range (list): Threshold range to plot.
            ax (pyplot.axes): Axes to plot on. Otherwise, plot on the default.
    Post:
        If ax was passed, this function will modify ax in place to contain the
        cross section plot. If ax was not passed, this function modifies the
        matplotlib current set of axes.
    """
    srea = df.loc[df['execution'] == "srea"]
    drea = df.loc[df['execution'] == "drea"]

    naming = "drea-ara"
    ara = df.loc[(df['execution'] == naming)]

    if "threshold_range" in kwargs:
        thresholds = kwargs["threshold_range"]
    else:
        thresholds = [0.0, 0.0625, 0.125, 0.25, 0.375, 0.5, 0.75, 1.0]
    # End setup ---------------------------------------------------------------
    data = threshold_means(ara, "ar_threshold", thresholds,
                            drea, error_fac=ERROR_FAC)

    #if using_sc:
    #    aralabel = "ARSC ".format(ar_cut)
    #else:
    #    aralabel = "ARSC ".format(sc_cut)
    aralabel = "DREA-AR Alt "
    srea_rob = srea["robustness"].mean()
    drea_rob = drea["robustness"].mean()
    if "ax" in kwargs:
        ax = kwargs["ax"]
    else:
        ax = plt.gca()
    ax.errorbar(thresholds, data.robs, yerr=data.robs_err,
                linestyle='-',
                 capsize=4, linewidth=1,
                 label=aralabel + "Robustness")
    ax.errorbar(thresholds, data.res, linestyle='-.',
                yerr=data.res_err, linewidth=1,
                capsize=4,
                label=aralabel + "Reschedules")
    ax.plot(thresholds, data.runtimes, linestyle=':', linewidth=1,
             label=aralabel + "Runtime")

    try:
        if kwargs["plot_srea"]:
            ax.plot([0.0, 1.0], [srea_rob/drea_rob*100]*2,
                    dashes=(4, 3, 2, 3),
                    label="SREA Robustness",
                    color="k",
                    linewidth=1)
    except KeyError:
        pass
    #ax.legend(loc="lower center")
    ax.legend(loc="lower left")
    #ax.title(aralabel+"Cross Section")
    ax.set_xlabel("Threshold")
    ax.set_ylabel("Percent of DREA")
    ax.set_xlim(X_AXIS_RANGE)
    ax.set_ylim(Y_AXIS_RANGE)

    if not "ax" in kwargs:
        plt.show()
