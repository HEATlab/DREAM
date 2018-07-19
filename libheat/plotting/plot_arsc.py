"""This file holds functions which plot ARSC results for the conference paper

"""


import matplotlib.pyplot as plt


X_AXIS_RANGE = (-0.02, 1.02)
Y_AXIS_RANGE = (-10, 120)
ERROR_FAC = 1.96


def plot_arsc_cross(df, **kwargs):
    """ Plot ARSC algorithm crossection.
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
    if not "sc_threshold" in kwargs and not "ar_threshold" in kwargs:
        raise ValueError("Requires either 'sc_threshold' or 'ar_threshold' set"
                         " when using ARSI algorithm")
    elif not "sc_threshold" in kwargs:
        # sc cross section not present, must be using SC
        using_sc = True
        ar_cut= kwargs["ar_threshold"]
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


    srea_rob = srea["robustness"]
    drea_rob = drea["robustness"]
    arsc_rob = arsc["robustness"]


    if "threshold_range" in kwargs:
        thresholds = kwargs["threshold_range"]
    else:
        thresholds = [0.0, 0.0625, 0.125, 0.25, 0.375, 0.5, 0.75, 1.0]
    # End setup ---------------------------------------------------------------
    drea_res = drea["reschedule_freq"].mean()
    drea_send = drea["send_freq"].mean()
    drea_run = drea["runtime"].mean()

    rob_means = []
    stderrs = []
    sends = []
    sends_err = []
    reschedules = []
    reschedules_err = []
    runtimes = []

    for t in thresholds:
        if using_sc:
            try:
                arsc_point = arsc.loc[arsc["sc_threshold"] == t]
            except KeyError:
                arsc_point = arsc.loc[arsc["si_threshold"] == t]
        else:
            arsc_point = arsc.loc[arsc["ar_threshold"] == t]
        mean = arsc_point["robustness"].mean()/drea_rob.mean() * 100
        rob_means.append(mean)
        se = arsc_point["robustness"].sem() * 100
        stderrs.append(se*ERROR_FAC)
        send_dat = arsc_point["send_freq"].mean()/drea_send * 100
        sends.append(send_dat)
        send_err = arsc_point["send_freq"].sem() * 100
        sends_err.append(send_err*ERROR_FAC)
        res = arsc_point["reschedule_freq"].mean()/drea_res * 100
        reschedules.append(res)
        res_err = arsc_point["reschedule_freq"].sem() * 100
        reschedules_err.append(res_err*ERROR_FAC)
        runtime = arsc_point["runtime"].mean()/drea_run * 100
        runtimes.append(runtime)

    #if using_sc:
    #    arsc_label = "ARSC ".format(ar_cut)
    #else:
    #    arsc_label = "ARSC ".format(sc_cut)
    arsc_label = "ARSC "
    if "ax" in kwargs:
        ax = kwargs["ax"]
        ax.errorbar(thresholds, rob_means, yerr=stderrs, linestyle='-',
                     capsize=4, linewidth=1,
                     label=arsc_label + "Robustness")
        if using_sc:
            ax.errorbar(thresholds, sends, yerr=sends_err, linestyle='-.',
                        linewidth=1,
                        capsize=4,
                        label=arsc_label + "Sent Schedules")
        else:
            ax.errorbar(thresholds, reschedules, linestyle='-.',
                        yerr=reschedules_err, linewidth=1,
                        capsize=4,
                        label=arsc_label + "Reschedules")
        ax.plot(thresholds, runtimes, linestyle=':', linewidth=1,
                 label=arsc_label + "Runtime")

        try:
            if kwargs["plot_srea"]:
                ax.plot([0.0, 1.0], [srea["robustness"].mean()
                                     /drea_rob.mean()*100]*2,
                        dashes=(4, 3, 2, 3),
                        label="SREA Robustness",
                        color="k",
                        linewidth=1)
        except KeyError:
            pass

        #ax.legend(loc="lower center")
        ax.legend(loc="lower left")
        #ax.title(arsc_label+"Cross Section")
        if using_sc:
            ax.set_xlabel("SC Threshold")
        else:
            ax.set_xlabel("AR Threshold")
        ax.set_ylabel("Percent of DREA")
        ax.set_xlim(X_AXIS_RANGE)
        ax.set_ylim(Y_AXIS_RANGE)
    else:
        plt.errorbar(thresholds, rob_means, yerr=stderrs, linestyle='-',
                     capsize=4, linewidth=1,
                     label=arsc_label + "Robustness")
        plt.plot(thresholds, sends, linestyle='-.', linewidth=1,
                 label=arsc_label + "Sent Schedules")
        plt.plot(thresholds, runtimes, linestyle=':', linewidth=1,
                 label=arsc_label + "Runtime")

        plt.legend(loc="lower center")
        plt.title(arsc_label+"Cross Section")
        if using_sc:
            plt.xlabel("SC Threshold")
        else:
            plt.xlabel("AR Threshold")
        plt.ylabel("Percent of DREA")
        plt.xlim(X_AXIS_RANGE)
        plt.ylim(Y_AXIS_RANGE)
        plt.show()
