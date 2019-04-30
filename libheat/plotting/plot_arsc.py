"""This file holds functions which plot ARSC results for the conference paper

"""


import matplotlib.pyplot as plt


from .plot_utils import threshold_means


X_AXIS_RANGE = (-0.02, 1.02)
Y_AXIS_RANGE = (-10, 120)
ERROR_FAC = 1.96


def plot_arsc_cross(df, **kwargs):
    """Plot ARSC algorithm crossection.
    Args:
        df (DataFrame): DataFrame object to read from.
        **kwargs:
            sc_threshold (float): Holding si_value.
            ar_threshold (float): Holding ar_value.
            threshold_range (list): Threshold range to plot.
            ax (pyplot.axes): Axes to plot on. Otherwise, plot on the default.
    Post:
        If ax was passed, this function will modify ax in place to contain the
        cross section plot. If ax was not passed, this function modifies the
        matplotlib current set of axes.
    """
    # Start setup -------------------------------------------------------------
    if "sc_threshold" not in kwargs and "ar_threshold" not in kwargs:
        raise ValueError("Requires either 'sc_threshold' or 'ar_threshold' set"
                         " when using ARSI algorithm")
    elif "sc_threshold" not in kwargs:
        # sc cross section not present, must be using SC
        using_sc = True
        ar_cut = kwargs["ar_threshold"]
    else:
        # Must be using AR then
        using_sc = False
        sc_cut = kwargs["sc_threshold"]

    srea = df.loc[df['execution'] == "srea"]
    drea = df.loc[df['execution'] == "drea"]

    # Check naming of arsi/arsc
    naming = "arsc"
    if df.loc[df['execution'] == "arsc"].empty:
        naming = "arsi"

    if using_sc:
        arsc = df.loc[(df['execution'] == naming)
                      & (df["ar_threshold"] == ar_cut)]
    else:
        if naming == "arsi":
            arsc = df.loc[(df['execution'] == naming)
                          & (df["si_threshold"] == sc_cut)]
        else:
            arsc = df.loc[(df['execution'] == naming)
                          & (df["sc_threshold"] == sc_cut)]

    if "threshold_range" in kwargs:
        thresholds = kwargs["threshold_range"]
    else:
        thresholds = [0.0, 0.0625, 0.125, 0.25, 0.375, 0.5, 0.75, 1.0]
    # End setup ---------------------------------------------------------------

    if using_sc:
        try:
            data = threshold_means(arsc, "sc_threshold", thresholds,
                                   drea, error_fac=ERROR_FAC)
        except KeyError:
            data = threshold_means(arsc, "si_threshold", thresholds,
                                   drea, error_fac=ERROR_FAC)
    else:
        data = threshold_means(arsc, "ar_threshold", thresholds,
                               drea, error_fac=ERROR_FAC)

    # if using_sc:
    #    arsc_label = "ARSC ".format(ar_cut)
    # else:
    #    arsc_label = "ARSC ".format(sc_cut)
    arsc_label = "DREAM "
    srea_rob = srea["robustness"].mean()
    drea_rob = drea["robustness"].mean()
    if "ax" in kwargs:
        ax = kwargs["ax"]
        ax.errorbar(thresholds, data.robs, yerr=data.robs_err,
                    linestyle='-',
                    capsize=4, linewidth=1,
                    label=arsc_label + "Robustness")
        if using_sc:
            ax.errorbar(thresholds, data.sends, yerr=data.sends_err,
                        linestyle='-.',
                        linewidth=1,
                        capsize=4,
                        label=arsc_label + "Sent Schedules")
        else:
            ax.errorbar(thresholds, data.res, linestyle='-.',
                        yerr=data.res_err, linewidth=1,
                        capsize=4,
                        label=arsc_label + "Reschedules")
        ax.plot(thresholds, data.runtimes, linestyle=':', linewidth=1,
                label=arsc_label + "Runtime")

        try:
            if kwargs["plot_srea"]:
                ax.plot([0.0, 1.0], [srea_rob / drea_rob * 100] * 2,
                        dashes=(4, 3, 2, 3),
                        label="SREA Robustness",
                        color="k",
                        linewidth=1)
        except KeyError:
            pass

        ax.legend(loc="lower left", framealpha=0.2)
        #ax.title(arsc_label+"Cross Section")
        if using_sc:
            ax.set_xlabel("SC Threshold")
        else:
            ax.set_xlabel("AR Threshold")
        ax.set_ylabel("Percent of DREA")
        ax.set_xlim(X_AXIS_RANGE)
        ax.set_ylim(Y_AXIS_RANGE)
    else:
        plt.errorbar(thresholds, data.robs, yerr=data.robs_err, linestyle='-',
                     capsize=4, linewidth=1,
                     label=arsc_label + "Robustness")
        plt.plot(thresholds, data.sends, linestyle='-.', linewidth=1,
                 label=arsc_label + "Sent Schedules")
        plt.plot(thresholds, data.runtimes, linestyle=':', linewidth=1,
                 label=arsc_label + "Runtime")

        plt.legend(loc="lower center")
        plt.title(arsc_label + "Cross Section")
        if using_sc:
            plt.xlabel("SC Threshold")
        else:
            plt.xlabel("AR Threshold")
        plt.ylabel("Percent of DREA")
        plt.xlim(X_AXIS_RANGE)
        plt.ylim(Y_AXIS_RANGE)
        plt.show()
