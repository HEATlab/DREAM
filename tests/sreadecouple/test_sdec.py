import unittest


import libheat.decoupling.sreadecouple as sreadecouple
import libheat.stntools as stntools
from libheat.dmontsim import DecoupledSimulator
from libheat.montsim import Simulator


STN1 = "test_data/two_agent_sync.json"
STN2 = "test_data/two_agent_sync2.json"
STN3 = "test_data/two_agent_stretch.json"


class TestSdecDecouple(unittest.TestCase):
    def test_sdec_case_1(self):
        stn = stntools.load_stn_from_json_file(STN1)["stn"]
        alpha, subproblems = sreadecouple.decouple_agents(stn)
        self.assertTrue(0.505 <= alpha <= 0.506)
        self.assertEqual(len(subproblems), 2)
        for g in subproblems:
            self.assertEqual(g.get_assigned_time(0), 0)

    def test_sdec_case_2(self):
        stn = stntools.load_stn_from_json_file(STN2)["stn"]
        alpha, subproblems = sreadecouple.decouple_agents(stn)
        self.assertTrue(0.0 <= alpha <= 0.01)
        self.assertEqual(len(subproblems), 2)
        for g in subproblems:
            self.assertEqual(g.get_assigned_time(0), 0)

    def test_decouple_sim(self):
        stn = stntools.load_stn_from_json_file(STN1)["stn"]
        sim = DecoupledSimulator(random_seed=42)
        self.assertTrue(sim.simulate(stn, decouple_type="srea"))

    def test_decouple_sim_check_equal1(self):
        stn = stntools.load_stn_from_json_file(STN1)["stn"]
        sim1 = DecoupledSimulator(random_seed=42)
        sim2 = Simulator(random_seed=42)
        for i in range(10):
            # Decoupled sim must be identical to SREA in this one STN.
            self.assertEqual(sim1.simulate(stn, decouple_type="srea"),
                             sim2.simulate(stn, "srea"))

    def test_decouple_sim_check_equal2(self):
        stn = stntools.load_stn_from_json_file(STN3)["stn"]
        sim1 = DecoupledSimulator(random_seed=42)
        sim2 = Simulator(random_seed=42)
        for i in range(10):
            # Decoupled sim must be identical to SREA in this one STN.
            res1 = sim1.simulate(stn, decouple_type="srea")
            res2 = sim2.simulate(stn, "srea")
            self.assertEqual(res1, res2)

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
