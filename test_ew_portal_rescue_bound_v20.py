#!/usr/bin/env python3
import unittest

import ew_portal_rescue_bound_v20 as mod


class EWPortalRescueBoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_report_executes(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])

    def test_signed_floor_and_historical_curvature(self):
        numerical = self.report["numerical"]
        self.assertEqual(numerical["signed_guaranteed_invariant_floor"], 34)
        self.assertEqual(numerical["physical_h_GeV"], 174.0)
        self.assertLess(
            numerical["historical_direct_HH_curvature_GeV2"], -1.0e30
        )

    def test_guaranteed_H4_rescue_is_nonperturbative(self):
        numerical = self.report["numerical"]
        self.assertEqual(numerical["guaranteed_H4_channels"], 2)
        self.assertGreater(numerical["required_total_H4_coupling"], 1.0e20)
        self.assertGreater(
            numerical["required_over_combined_perturbative_allowance"], 1.0e20
        )
        self.assertLess(
            numerical["best_case_rescued_HH_curvature_GeV2"], 0.0
        )

    def test_scope(self):
        flags = self.report["flag"]
        self.assertTrue(
            flags["historical_lam4_point_excluded_within_signed_floor34"]
        )
        self.assertTrue(
            flags["guaranteed_even_H2_portals_cannot_directly_rescue"]
        )
        self.assertTrue(
            flags["guaranteed_H4_channels_insufficient_perturbatively"]
        )
        self.assertTrue(
            flags["unknown_beyond_floor_odd_H_channel_or_new_mechanism_required"]
        )
        self.assertTrue(flags["mechanical_floor37_rejected"])
        self.assertFalse(flags["full_invariant_ring_complete"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
