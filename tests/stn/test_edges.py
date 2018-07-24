import unittest

import libheat.stntools as stntools


class TestEdges(unittest.TestCase):

    def test_stn_edge_creation(self):
        edge1 = stntools.Edge(0, 1, 4, 10)
        edge2 = stntools.Edge(0, 1, 4, 10)
        self.assertTrue(edge1 == edge2)

        edge3 = stntools.Edge(0, 1, 4, 10, distribution="N_5_1")
        self.assertTrue(edge1 != edge3)

if __name__ == "__main__":
    unittest.main()
