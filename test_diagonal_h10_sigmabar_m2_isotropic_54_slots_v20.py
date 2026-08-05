#!/usr/bin/env python3
import unittest

import diagonal_h10_sigmabar_m2_isotropic_54_slots_v20 as mod


class DiagonalIsotropic54SlotsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        flags = self.report["flag"]
        self.assertTrue(flags["isotropic_norm_54_slots_partially_filled"])
        self.assertTrue(flags["schur_fed_with_partial_A_C"])
        self.assertFalse(flags["diagonal_h10_m2_fully_derived"])
        self.assertFalse(flags["diagonal_sigmabar_m2_fully_derived"])
        self.assertFalse(flags["cg_tensors_120_320_4125_invented"])
        self.assertFalse(flags["full_invariant_ring"])
        self.assertFalse(flags["full_component_hessian"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_partial_shapes_positive(self):
        self.assertEqual(len(self.report["A_partial_GeV2"]), 10)
        self.assertEqual(len(self.report["C_partial_GeV2"]), 126)
        self.assertGreater(min(self.report["A_partial_GeV2"]), 0.0)
        self.assertGreater(min(self.report["C_partial_GeV2"]), 0.0)

    def test_five_slots_and_open_remainder(self):
        filled = self.report["partial_diagonals"]["filled_slots"]
        self.assertEqual(len(filled), 5)
        for key in (
            "OPEN_H10_SOFT_OR_NORM",
            "OPEN_H10_FROM_210_NORM",
            "OPEN_SIGMA_FROM_210_NORM",
            "OPEN_H10_54",
            "OPEN_126_54_LOCKING",
        ):
            self.assertIn(key, filled)
        open_slots = self.report["partial_diagonals"]["still_open_slots"]
        self.assertIn("OPEN_MIXED_120", open_slots)
        self.assertIn("OPEN_126_4125", open_slots)

    def test_schur_report_present(self):
        sch = self.report["schur_with_partial_diagonals"]
        self.assertIn("positive_definite", sch)
        self.assertIn("largest_normalized_singular_value", sch)
        self.assertEqual(self.report["portal_B"]["shape"], [10, 126])


if __name__ == "__main__":
    unittest.main()
