#!/usr/bin/env python3
"""Tests for (p,a,ω) promotion into reduced amplitudes."""

from __future__ import annotations

import unittest

import promote_paw_split_reduced_amplitudes_v20 as mod


class PromotePawSplitReducedAmplitudesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertFalse(self.report["flags"]["whole_model_validated"])
        self.assertFalse(self.report["flags"]["g1_closed"])
        self.assertFalse(self.report["flags"]["mixed_field_cg_invented"])

    def test_promotion_wires_seven_amplitudes(self):
        self.assertTrue(self.report["flags"]["paw_split_promoted_into_reduced_amplitudes"])
        self.assertEqual(len(self.report["promoted_fields"]), 7)
        self.assertNotIn("P_210", self.report["promoted_fields"])
        self.assertTrue(self.report["checks"]["pure210_block_psd"])
        self.assertTrue(
            self.report["promoted_hessian_lam4_0"]["positive_semidefinite"]
        )
        self.assertTrue(self.report["ray_consistency_vs_insertion"]["consistent"])
        self.assertTrue(self.report["flags"]["linear_cg_px_cross_for_Delta_H10"])
        self.assertFalse(self.report["flags"]["isotropic_P_cross_proxy_only"])
        self.assertTrue(self.report["flags"]["isotropic_residual_S_Phi17_only"])
        self.assertTrue(self.report["checks"]["linear_cg_Delta_H10_matched_at_vacuum"])
        self.assertTrue(
            self.report["remaining_blockers"]["published_linear_cg_for_S_Phi17_cross"]
        )

if __name__ == "__main__":
    unittest.main()
