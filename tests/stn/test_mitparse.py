import unittest
import numpy as np

import libheat.stntools as stntools


MIT_STN1 = "test_data/stp_picard.json"
MIT_STN2 = "test_data/stp_picard_uniform.json"


class TestMitParse(unittest.TestCase):
    def test_read1(self):
        stn = stntools.mit2stn(MIT_STN1)[0]
        self.assertEqual(len(stn.verts.keys()), 4)
        self.assertEqual(len(stn.edges.keys()), 3)
        self.assertEqual(stn.edges[(0, 1)].distribution, "N_20.0_2.0")
        self.assertEqual(stn.edges[(2, 3)].distribution, "N_60.0_5.0")

    def test_read2(self):
        stn = stntools.mit2stn(MIT_STN2, add_z=True, connect_origin=True)[0]
        self.assertEqual(len(stn.verts.keys()), 5)
        self.assertEqual(len(stn.edges.keys()), 7)
        self.assertEqual(stn.edges[(1, 2)].distribution, "U_1.0_5.0")
        self.assertEqual(stn.edges[(3, 4)].distribution, "U_6.0_12.0")
        stn.floyd_warshall()

    def test_sample1(self):
        state1 = np.random.RandomState(42)
        state2 = np.random.RandomState(42)
        stn1 = stntools.mit2stn(MIT_STN1)[0]
        stn2 = stntools.mit2stn(MIT_STN1)[0]
        for e in stn1.contingent_edges.keys():
            stn1.contingent_edges[e].resample(state1)
            stn2.contingent_edges[e].resample(state2)
            self.assertEqual(stn1.contingent_edges[e].sampled_time(),
                             stn2.contingent_edges[e].sampled_time())

    def test_sample2(self):
        state1 = np.random.RandomState(42)
        state2 = np.random.RandomState(42)
        stn1 = stntools.mit2stn(MIT_STN2)[0]
        stn2 = stntools.mit2stn(MIT_STN2)[0]
        for e in stn1.contingent_edges.keys():
            stn1.contingent_edges[e].resample(state1)
            stn2.contingent_edges[e].resample(state2)
            self.assertEqual(stn1.contingent_edges[e].sampled_time(),
                             stn2.contingent_edges[e].sampled_time())


if __name__ == "__main__":
    unittest.main()
