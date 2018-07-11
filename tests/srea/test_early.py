import unittest


import libheat.srea as srea
from libheat.montsim import Simulator
import libheat.stntools as stntools

STN1 = "test_data/two_agent_sync.json"

class TestEarlySimulator(unittest.TestCase):
    def test_early_sim(self):
        stn = stntools.load_stn_from_json_file(STN1)["stn"]
        sim = Simulator(42)
        successes = 0
        res = 100
        for i in range(res):
            result = sim.simulate(stn, execution_strat="early")
            if result:
                successes += 1
        robustness = successes/res
        self.assertTrue(0.10 < robustness < 0.20)


if __name__ == "__main__":
    unittest.main()
