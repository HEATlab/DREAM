"""
This simply tests the STNs
"""

import optdecouple
import stntools

stn_file = "/home/crystal/robotbrunch/handmade_stns/two_agent_T_normal.json"
s = stntools.load_stn_from_json_file(stn_file)["stn"]

optdecouple.optimal_decouple_agents(s)
