import pulp


from .stntools import STN


Z_VERT_ID = 0


def wilson_flex_pstn(stn) -> float:
    """ Calculate Wilson Flexibility for PSTN or STNUs.
    Notes:
        The provided STN must be fully connected and consistent.
        Contingent timepoints are ignored, as they have no flexibility.
    Args:
        stn: A simple temporal network to calculate the flexibility of.
    Returns:
        Returns a float indicating the Wilson flexibility of the network.
    """

    # Dict which holds vertex time bounds for Linear Program variables.
    bounds = {}

    problem = pulp.LpProblem("Wilson Flexibility", pulp.LpMaximize)
    # Add all vertices of the graph to the LP.
    for i in range(len(stn.get_all_verts())):
        var_name_low = "t{}-".format(i)
        var_name_high = "t{}+".format(i)
        upper_bound = stn.get_edge_weight(Z_VERT_ID, i)
        low_bound = -stn.get_edge_weight(i, Z_VERT_ID)

        # Create the variables in the LP.
        bounds[(i, "-")] = pulp.LpVariable(var_name_low, lowBound=low_bound)
        bounds[(i, "+")] = pulp.LpVariable(var_name_high, upBound=upper_bound)

        # Add the Z constraints to the LP.
        # Line one of the Wilson LP on line 35.
        problem += bounds[(i, "+")] >= bounds[(i, "-")]

    # Add all edges to the graph LP.
    for vert_pair, cons in stn.get_edges():
        # TODO:
        pass

    # Compute the differences of all of the bounds.
    # Note, we should only do this for non-contingent timepoints.
    bound_diffs = []]
    for key in bounds.keys():
        if key[0] in stn.
        bounds[(i, "+")] - bounds[(i, "-")]
    req_sum = sum([bounds[] ])
