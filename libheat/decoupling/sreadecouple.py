import pulp


from ..stntools import STN, Edge
from ..stntools.distempirical import invcdf_norm
from ..srea import srea


def decouple_agents(stn: STN):
    """Decouples agents optimally (maximising flexibility between agents)

    Args:
    stn (:obj:`STN`): STN to optimally decouple using.

    Returns:
        A tuple of the form (alpha, guide STN), where the alpha is the amount
        of risk associated with that guide. The guide is a decomposition, and
        often we want only the the interagent agent decoupling constraints.
    """
    results = srea(stn)
    if results is None:
        # SREA failed, so consider this a special case.
        return 0.0, None
    alpha = results[0]
    guide = results[1]
    return alpha, extract_substns(stn, guide)

def extract_substns(stn: STN, guide: STN):
    new_stn = apply_decoupling_constraints(stn, guide)
    substns = []
    for a in stn.agents:
        substns.append(new_stn.get_agent_substn(a, True))
    return substns


def apply_decoupling_constraints(stn: STN, guide: STN) -> STN:
    """Creates a copy of the provided stn, but adds decoupling constraints
    from the guide.

    Args:
        stn (:obj:`STN`): STN to copy
        guide (:obj:`STN`): STN to use fro decoupling constraints.

    Returns:
        Returns a copy of `stn` but with decoupling constraints extracted
        from guide.
    """
    stncopy = stn.copy()
    # Extract the edge weights from the guide, and apply them to the copy.
    for from_id, to_id in guide.interagent_edges.keys():
        from_max = guide.get_edge_weight(0, from_id)
        from_min = -guide.get_edge_weight(from_id, 0)
        to_max = guide.get_edge_weight(0, to_id)
        to_min = -guide.get_edge_weight(to_id, 0)
        stncopy.update_edge(0, from_id, from_max)
        stncopy.update_edge(from_id, 0, -from_min)
        stncopy.update_edge(0, to_id, to_max)
        stncopy.update_edge(to_id, 0, -to_min)
    return stncopy
