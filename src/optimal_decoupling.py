import pulp
from stntools import STN, Edge

def optimal_decouple_agents(stn):
    """ Optimally decouple agents.
    """
    prob = lp_setup(stn)
    prob.writeLP("/tmp/OptimalDecoupling.lp")
    prob.solve()
    status = pulp.LpStatus[prob.status]
    print("status: {}".format(status))
    if status == "Optimal":
        for v in prob.variables():
            print("{} = {}".format(v.name, v.varValue))

def lp_setup(stn):
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
        #pass
        z_cons = dual_events[(i, "+")] >= dual_events[(i, "-")]
        prob += z_cons
        #prob += dual_events[(i, "+")] >= 0
        #prob += dual_events[(i, "+")] >= dual_events[(i, "-")]
    # Add constraints between min and maxes.
    for i, j in stn.edges.keys():
        # Wilson et al. Theorem 1 LP line 2.
        const_ij = (dual_events[(j, "+")] - dual_events[(i, "-")]
                    <= stn.get_edge_weight(i, j))
        const_ji = (dual_events[(i, "+")] - dual_events[(j, "-")]
                    <= stn.get_edge_weight(j, i))
        print(const_ij)
        print(const_ji)
        prob += const_ij
        prob += const_ji

    inter_edges = stn.interagent_edges


    # TODO: This should be a set.
    synchrony_points = []
    for e in inter_edges:
        if not e.i in synchrony_points:
            synchrony_points.append(i)
        if not e.j in synchrony_points:
            synchrony_points.append(j)
    print(synchrony_points)
    if synchrony_points == []:
        print("No synchrony points")
        synchrony_points = [0, 1, 2]
    # We only want to sum up the synchrony points.
    prob_sum = sum([dual_events[(i, "+")] - dual_events[(i, "-")]
                   for i in synchrony_points])

    prob += prob_sum, "Info"
    return prob

def extract_decoupling(stn) -> Edge:
    pass
