import unittest


import libheat.srea as srea
from libheat.montsim import Simulator
import libheat.stntools as stntools

STN1 = "test_data/two_agent_sync.json"
STN2 = "test_data/two_contingent.json"
STN3 = "test_data/two_agent_sync_uniform_1.json"
STN4 = "test_data/two_agent_sync_uniform_2.json"


class TestSreaSimulator(unittest.TestCase):

    def test_srea_case_1(self):
        stn = stntools.load_stn_from_json_file(STN1)["stn"]
        alpha, guide = srea.srea(stn)
        self.assertTrue(0.504 < alpha < 0.508)

    def test_srea_case_2(self):
        stn = stntools.load_stn_from_json_file(STN2)["stn"]
        alpha, guide = srea.srea(stn)
        self.assertEqual(guide.get_assigned_time(1), 0.0)
        self.assertEqual(alpha, 0.481)

    def test_srea_case_uniform_1(self):
        """Test two agent sync with uniform dists, easy solution."""
        stn = stntools.load_stn_from_json_file(STN3)["stn"]
        alpha, guide = srea.srea(stn)
        self.assertEqual(guide.get_assigned_time(1), 0.0)
        self.assertEqual(alpha, 0.0)

    def test_srea_case_uniform_2(self):
        """Test two agent sync with uniform dists, no solution."""
        stn = stntools.load_stn_from_json_file(STN4)["stn"]
        result = srea.srea(stn)
        # We expect this one to never give a guide. It's impossible
        # to succeed, and thus inconsistent.
        self.assertEqual(result, None)

    def test_srea_sim_1(self):
        stn = stntools.load_stn_from_json_file(STN1)["stn"]
        sim = Simulator(42)
        successes = 0
        res = 50
        for i in range(res):
            result = sim.simulate(stn, execution_strat="srea")
            if result:
                successes += 1
        robustness = successes / res
        self.assertTrue(0.60 < robustness < 0.80)

    def test_srea_sim_2(self):
        stn = stntools.load_stn_from_json_file(STN2)["stn"]
        sim = Simulator(42)
        successes = 0
        res = 50
        for i in range(res):
            result = sim.simulate(stn, execution_strat="srea")
            if result:
                successes += 1
        robustness = successes / res
        # we expect 0.682
        self.assertTrue(0.63 < robustness < 0.72)


if __name__ == "__main__":
    unittest.main()
