import pulp


from .stntools import STN, Edge


def optimal_decouple_agents(stn):
    """ Optimally decouple agents.
    """
    pulp.LpSolverDefault.msg = 1
    _, assignments = wilson_flex(stn)
    print("Got here!")

def wilson_flex(stn: STN):
    """ Calculate Wilson Flexibility Decoupling """
    prob, dual_events = _wilson_lp_setup(stn)
    diffs = [dual_events[(i, "+")] - dual_events[(i, "-")]
             for i in stn.verts.keys()]
    prob_sum = sum(diffs)
    prob += prob_sum, "Maximise the differences within dual constraints"
    prob.writeLP("/tmp/wilson_flex.lp")
    prob.solve()
    # Check the status of the LP.
    status = pulp.LpStatus[prob.status]
    if status != "Optimal":
        return (None, None)

    assignments = _get_lp_assignments(prob)
    return pulp.value(prob.objective), assignments


def synchrony_maximize(stn: STN):
    """ Creates and sets up a Wilson LP to maximise interagent flexibility.
    """
    prob, dual_events = _wilson_lp_setup(stn)
    synchrony_pairs = stn.interagent_edges.keys()
    # Create a set of synchrony points.
    synchrony_points = set()
    for i, j in synchrony_pairs:
        if not i in synchrony_points:
            synchrony_points.add(i)
        if not j in synchrony_points:
            synchrony_points.add(j)
    print(synchrony_points)
    if synchrony_points == set():
        print("No synchrony points")
        return (None, None)
    # We only want to sum up the synchrony points.
    prob_sum = sum([dual_events[(i, "+")] - dual_events[(i, "-")]
                   for i in synchrony_points])
    # Set the optimisation function.
    prob += prob_sum, "Maximise the flexibility of interagent constraints"
    prob.solve()
    status = pulp.LpStatus[prob.status]
    if status != "Optimal":
        return (None, None)
    # Retrieve assignments of each of the LP variables, in a format that makes
    # sense for an STN.
    assignments = _get_lp_assignments(prob)
    return pulp.value(prob.objective), assignments


def _wilson_lp_setup(stn: STN):
    """ Sets up the Wilson et al. 2014 Linear Program (LP) and returns the PuLP
    problem.

    Note:
        By default, does not apply the maximasation function that the LP needs.

    Args:
        stn: STN object to use for the LP.

    Returns:
        Returns a tuple of the form (PuLP problem, dict), where the PuLP
        problem is the LP with the Wilson constraints applied, and the dict is
        a dictionary with elements {(i, "+/-"): LpVariable}, which allows
        extracting the t+ or t- LP variables used in the dual representation in
        the Wilson et al. Paper.
    """
    dual_events = {}
    prob = pulp.LpProblem("PSTN Optmial Decoupling (Wilson Edit)",
                          pulp.LpMaximize)

    # At somepoint we may not have keys.
    try:
        vert_gen = stn.verts.keys()
    except TypeError:
        vert_gen = stn.verts
    # Add constraints of z-edges
    for i in vert_gen:

        dual_events[(i, "+")] = pulp.LpVariable("t_{}_p".format(i),
            lowBound=None,
            upBound=float(stn.get_edge_weight(0, i))
        )
        dual_events[(i, "-")] = pulp.LpVariable("t_{}_n".format(i),
            lowBound=-float(stn.get_edge_weight(0, i)),
            upBound=None
        )
        # Add the constraint to the LpProblem
        # Note that the zero timepoint is automatically constrained to start at
        # zero because get_edge_weight returns 0 for (0, 0) connection.
        z_cons = dual_events[(i, "+")] >= dual_events[(i, "-")]
        if i == 0:
            print(dual_events[(i, "+")].upBound)
            print(dual_events[(i, "-")].lowBound)
        #prob += z_cons
    # Add constraints between min and maxes.
    for i, j in stn.edges.keys():
        # Wilson et al. Theorem 1 LP line 2.
        weight_ij = max(min(stn.get_edge_weight(i, j), 10.0**40), -10.0**40)
        const_ij = (dual_events[(j, "+")] - dual_events[(i, "-")]
                    <= weight_ij)
        weight_ji = max(min(stn.get_edge_weight(j, i), 10.0**40), -10.0**40)
        const_ji = (dual_events[(i, "+")] - dual_events[(j, "-")]
                    <= weight_ji)
        print("<begin> Constraints")
        print(const_ij)
        print(const_ji)
        print("<end> Constraints")
        prob += const_ij
        prob += const_ji

    return (prob, dual_events)


def _get_lp_assignments(prob):
    """ Retrieves edge assignments from the Linear Program problem """
    assignments = {}
    for v in prob.variables():
        try:
            name_list = v.name.split("_")
            event_num = int(name_list[1])
            sign_value = name_list[2]
        except ValueError:
            print("Could not split: {}".format(v.name))
            continue
        if sign_value == "p":
            try:
                assignments[(0, event_num)][1] = v.varValue
            except KeyError:
                assignments[(0, event_num)] = [-float("inf"), v.varValue]
        elif sign_value == "n":
            try:
                assignments[(0, event_num)][0] = v.varValue
            except KeyError:
                assignments[(0, event_num)] = [v.varValue, float("inf")]
        else:
            print("Dual sign not recognised: {}".format(sign_value))
            continue
    return assignments


def get_decouple_constraints(stn, assignments):
    """ Returns a set of STN Edge objects which represent interagent
    decoupling constraints

    Args:
        stn (STN):
        assignments (dict):
    """
    z_constraints = set()
    for edge_tuple in assignments.items():
        vert_from = edge_tuple[0][0]
        vert_to = edge_tuple[0][1]

        # Vert_from should always be 0, so we should be okay to assume such.
        assert (vert_from == 0)

        min_val = assignments[(vert_from, vert_to)][0]
        max_val = assignments[(vert_from, vert_to)][1]
        for inter in stn.interagent_edges.keys():
            new_edge = Edge(vert_from, vert_to, min_val, max_val)
            z_constraints.add(new_edge)
    return z_constraints
