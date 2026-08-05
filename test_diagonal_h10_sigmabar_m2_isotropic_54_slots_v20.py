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
        self.assertTrue(flags["isotropic_norm_slots_partially_filled"])
        self.assertFalse(flags["isotropic_norm_54_slots_partially_filled"])
        self.assertTrue(flags["unphysical_H10_MI_54_seed_withdrawn"])
        self.assertTrue(flags["schur_fed_with_partial_A_C"])
        self.assertFalse(flags["diagonal_h10_m2_fully_derived"])
        self.assertFalse(flags["diagonal_sigmabar_m2_fully_derived"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_partial_shapes_positive(self):
        self.assertEqual(len(self.report["A_partial_GeV2"]), 10)
        self.assertEqual(len(self.report["C_partial_GeV2"]), 126)
        self.assertGreater(min(self.report["A_partial_GeV2"]), 0.0)
        self.assertGreater(min(self.report["C_partial_GeV2"]), 0.0)

    def test_four_filled_two_withdrawn(self):
        partial = self.report["partial_diagonals"]
        self.assertEqual(len(partial["filled_slots"]), 4)
        self.assertEqual(len(partial["withdrawn_slots"]), 2)
        self.assertEqual(partial["components"]["locking_isotropic_seed"], 0.0)
        self.assertIn("OPEN_MIXED_126", partial["filled_slots"])
        self.assertNotIn("OPEN_MIXED_126", partial["still_open_slots"])
        self.assertNotIn("OPEN_MIXED_10", partial["still_open_slots"])
        self.assertIn("OPEN_MIXED_10", partial["absorbed_slots"])
        self.assertIn("OPEN_210_CHANNEL_54", partial["absorbed_slots"])
        self.assertIn("OPEN_210_CHANNEL_45", partial["absorbed_slots"])
        self.assertNotIn("OPEN_210_CHANNEL_54", partial["still_open_slots"])
        self.assertNotIn("OPEN_210_CHANNEL_45", partial["still_open_slots"])
        self.assertIn("OPEN_H10_54", partial["still_open_slots"])
        self.assertIn("OPEN_126_54_LOCKING", partial["still_open_slots"])
        self.assertIn("OPEN_210_CHANNEL_1050", partial["still_open_slots"])
        self.assertGreater(
            partial["filled_slots"]["OPEN_MIXED_126"]["contribution_GeV2"], 0.0
        )

    def test_schur_report_present(self):
        sch = self.report["schur_with_partial_diagonals"]
        self.assertIn("positive_definite", sch)
        self.assertIn("largest_normalized_singular_value", sch)
        self.assertEqual(self.report["portal_B"]["shape"], [10, 126])


if __name__ == "__main__":
    unittest.main()
