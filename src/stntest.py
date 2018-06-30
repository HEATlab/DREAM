import optimal_decoupling
import stntools

s = stntools.STN()
s.add_vertex(0, 0)
s.add_vertex(1, 0)
s.add_vertex(2, 0)
s.add_edge(0, 1, 0, 1000.0)
s.add_edge(0, 2, 100.0, 1000.0)

optimal_decoupling.optimal_decouple_agents(s)
