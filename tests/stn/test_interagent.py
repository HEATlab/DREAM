import unittest

import libheat.stntools as stntools


STN1 = "test_data/two_agent_sync.json"
STN2 = "test_data/two_contingent.json"


class TestInteragent(unittest.TestCase):

    def test_stn_interagent_edges(self):
        stn = stntools.load_stn_from_json_file(STN1)["stn"]
        self.assertEqual(list(stn.interagent_edges.keys()), [(2,4)])
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
