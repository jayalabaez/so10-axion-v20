#!/usr/bin/env python3
import unittest

import mixed_rep_invariant_exact_witness_v20 as mod


EXPECTED = {
    "H_self": -307552,
    "D_self": 95863431680,
    "P_H": -12582162,
    "P_D": 22545991512,
    "H_D": -260343648,
}


class ExactInvariantWitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_report_executes(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])

    def test_determinants_are_reproducible_and_nonzero(self):
        self.assertEqual(self.report["determinants"], EXPECTED)
        self.assertTrue(all(value != 0 for value in EXPECTED.values()))

    def test_scope(self):
        flags = self.report["flag"]
        self.assertTrue(flags["five_rank_two_sectors_exactly_witnessed"])
        self.assertFalse(flags["full_molien_series"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
