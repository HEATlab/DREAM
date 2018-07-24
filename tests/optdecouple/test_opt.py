import unittest


import libheat.optdecouple as optdecouple
import libheat.stntools as stntools
from libheat.montsim_decoupled import DecoupledSimulator


STN1 = "test_data/two_agent_sync.json"
STN2 = "test_data/two_agent_sync2.json"
STN3 = "test_data/two_agent_stretch.json"


class TestOptDecouple(unittest.TestCase):
    def test_opt_case_1(self):
        stn = stntools.load_stn_from_json_file(STN1)["stn"]
        alpha, subproblems = optdecouple.decouple_agents(stn,
            fidelity=0.001)
        self.assertTrue(0.505 <= alpha <= 0.506)
        for g in subproblems:
            self.assertEqual(g.get_assigned_time(0), 0)

    def test_opt_case_2(self):
        stn = stntools.load_stn_from_json_file(STN2)["stn"]
        alpha, subproblems = optdecouple.decouple_agents(stn,
            fidelity=0.001)
        self.assertTrue(0.0 <= alpha <= 0.01)
        for g in subproblems:
            self.assertEqual(g.get_assigned_time(0), 0)

    def test_decouple_sim(self):
        stn = stntools.load_stn_from_json_file(STN1)["stn"]
        sim = DecoupledSimulator(random_seed=42)
        self.assertTrue(sim.simulate(stn))

    def test_decouple_sim_2(self):
        stn = stntools.load_stn_from_json_file(STN3)["stn"]
        sim = DecoupledSimulator(random_seed=42)
        self.assertFalse(sim.simulate(stn))

    def test_decouple_sim_3(self):
        stn = stntools.load_stn_from_json_file(STN3)["stn"]
        sim = DecoupledSimulator(random_seed=1000)
        self.assertTrue(sim.simulate(stn))


if __name__ == "__main__":
    unittest.main()
