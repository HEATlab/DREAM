import pulp


from ..stntools import STN
from ..stntools.distempirical import invcdf_norm


def decouple_agents(stn: STN, fidelity=0.001):
    """Decouples agents optimally (maximising flexibility between agents)

    Args:
        stn (STN): STN to optimally decouple using.
        fidelity (float, optional):

    Returns:
        A tuple of the form (alpha, guide STN), where the alpha is the amount
        of risk associated with that guide. The guide is a decomposition, and
        often we want only the the interagent agent decoupling constraints.
    """
    alpha, assignments = alpha_binary_search(stn, fidelity)
    if assignments is None:
        return None, None
    restricted_stn = stn.copy()
    for from_id, to_id in stn.interagent_edges:
        restricted_stn.update_edge(0, from_id, assignments[from_id][1])
        restricted_stn.update_edge(from_id, 0, -assignments[from_id][0])
        restricted_stn.update_edge(0, to_id, assignments[to_id][1])
        restricted_stn.update_edge(to_id, 0, -assignments[to_id][0])

    substns = []
    for agent in restricted_stn.agents:
        substn = restricted_stn.get_agent_substn(agent, True)
        substns.append(substn)
    return alpha, substns


def alpha_binary_search(stn: STN, fidelity=0.001):
    """Use a binary search to find lowest alpha (STN guide risk)

    Args:
        stn (STN): STN to use for LP variable creation.
        fidelity (float, optional): Threshold when the alpha search is close
            enough. Default is 0.001.

    Returns:
        Tuple of (alpha, dict of assignments), where alpha is the lowest
        associated risk level of those assignments.
    """
    upper_bound = 1.0
    lower_bound = 0.0
    current_alpha = -1.0
    assignments = None
    while True:
        new_alpha = (upper_bound + lower_bound)/2
        if abs(new_alpha - current_alpha) <= fidelity:
            # We have found an acceptable alpha.
            break
        current_alpha = new_alpha
        # Check to see if the LP is feasible.
        interflex, assign_test = maximize_interagent_flex(stn, current_alpha)
        if interflex is None:
            lower_bound = current_alpha
        else:
            assignments = assign_test
            upper_bound = current_alpha
    if assignments is None:
        return (None, None)
    return current_alpha, assignments


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


def maximize_interagent_flex(stn: STN, alpha: float):
    """
    Create an LP problem to maximise interagent flexibility (the amount of
    time between interagent bounds)

    Args:
        stn (STN): STN to use for identifying interagent synchronous
            constraints.
        alpha (float): Alpha to use for contingent bounds.
    """
    prob, duals = _wilson_lp_setup(stn)
    apply_contingent_bounds(stn, prob, duals, alpha)

    synchrony_pairs = stn.interagent_edges.keys()
    # Create a set of synchrony points.
    synchrony_points = set()
    for i, j in synchrony_pairs:
        if i not in synchrony_points:
            synchrony_points.add(i)
        if j not in synchrony_points:
            synchrony_points.add(j)
    if synchrony_points == set():
        print("No synchrony points")
        return (None, None)
    # We only want to sum up the synchrony points.
    prob_sum = sum([duals[(i, "+")] - duals[(i, "-")]
                    for i in synchrony_points])
    # Set the optimisation function.
    prob += prob_sum, "Maximise the flexibility of interagent constraints"
    prob.solve()
    if pulp.LpStatus[prob.status] == "Optimal":
        assignments = _get_lp_assignments(prob)
        return (pulp.value(prob.objective), assignments)
    return (None, None)


def apply_contingent_bounds(stn: STN, prob, variables: dict, alpha: float):
    """Apply the contingent constraints set by an alpha value"""

    for (i, j), edge in list(stn.contingent_edges.items()):
        p_ij = invcdf_norm(1.0-alpha*0.5, edge.mu, edge.sigma)
        p_ji = -invcdf_norm(alpha*0.5, edge.mu, edge.sigma)

        # Lund et al. LP (3)
        con3 = (variables[(j, '+')] - variables[(i, '+')] == p_ij)
        prob += con3
        # Lund et al. LP (4)
        con4 = (variables[(i, '-')] - variables[(j, '-')] == p_ji)
        prob += con4


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
                                                lowBound=-
                                                float(
                                                    stn.get_edge_weight(i, 0)),
                                                upBound=float(
                                                    stn.get_edge_weight(0, i))
                                                )
        dual_events[(i, "-")] = pulp.LpVariable("t_{}_n".format(i),
                                                lowBound=-
                                                float(
                                                    stn.get_edge_weight(i, 0)),
                                                upBound=float(
                                                    stn.get_edge_weight(0, i))
                                                )
        # Add the constraint to the LpProblem
        # Note that the zero timepoint is automatically constrained to start at
        # zero because get_edge_weight returns 0 for (0, 0) connection.
        z_cons = dual_events[(i, "+")] >= dual_events[(i, "-")]
        prob += z_cons
    # Add constraints between min and maxes.
    for i, j in stn.edges.keys():
        # Wilson et al. Theorem 1 LP line 2.
        weight_ij = max(min(stn.get_edge_weight(i, j), 10.0**40), -10.0**40)
        const_ij = (dual_events[(j, "+")] - dual_events[(i, "-")]
                    <= weight_ij)
        weight_ji = max(min(stn.get_edge_weight(j, i), 10.0**40), -10.0**40)
        const_ji = (dual_events[(i, "+")] - dual_events[(j, "-")]
                    <= weight_ji)
        prob += const_ij
        prob += const_ji

    return (prob, dual_events)


def _get_lp_assignments(prob):
    """Retrieves edge assignments from the Linear Program problem
        Assignment dictionary is of the form {(event_id), [min, max]}.
    """
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
                assignments[(event_num)][1] = v.varValue
            except KeyError:
                assignments[(event_num)] = [-float("inf"), v.varValue]
        elif sign_value == "n":
            try:
                assignments[(event_num)][0] = v.varValue
            except KeyError:
                assignments[(event_num)] = [v.varValue, float("inf")]
        else:
            print("Dual sign not recognised: {}".format(sign_value))
            continue
    return assignments


"""The below function does not work at all."""
# def get_decouple_constraints(stn, assignments):
#     """ Returns a set of STN Edge objects which represent interagent
#     decoupling constraints
#
#     Args:
#         stn (STN):
#         assignments (dict): Dict of the form {node_id: [min_time, max_time]}
#
#     Returns:
#         Returns a list of decoupling Edge objects.
#     """
#     z_constraints = set()
#     for edge_tuple in assignments.items():
#         vert_to = edge_tuple[0][1]
#
#         min_val = assignments[(0, vert_to)][0]
#         max_val = assignments[(0, vert_to)][1]
#         for inter in stn.interagent_edges.keys():
#             new_edge = Edge(vert_from, vert_to, min_val, max_val)
#             z_constraints.add(new_edge)
#     return z_constraints
