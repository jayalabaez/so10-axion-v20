#!/usr/bin/env python3
"""Tests for UV principle fixing coupling phases δ_i."""

from __future__ import annotations

import math
import unittest

import uv_delta_i_cp_reality_principle_v20 as mod


class UVDeltaICPRealityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "DELTA_I_FIXED_UNDER_CP_REALITY__SOFT_SCALE_AND_TAU_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["unique_delta_i_under_cp_reality_principle"])
        self.assertTrue(flags["rephasing_rank_2_one_physical_phase"])
        self.assertTrue(flags["delta_phys_equals_delta_lock_minus_2_delta_lam4"])
        self.assertTrue(flags["kappa_phase_absorbable"])
        self.assertTrue(flags["uv_selected_psi_fed_into_xy_width"])
        self.assertFalse(flags["unique_delta_i_model_independent"])
        self.assertFalse(flags["unique_soft_scale"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_rephasing_and_selection(self):
        reph = self.report["rephasing"]
        self.assertEqual(reph["rank"], 2)
        self.assertEqual(reph["n_physical_continuous"], 1)
        self.assertTrue(reph["all_demos_ok"])
        self.assertLess(reph["left_null_residual"], 1e-12)
        sel = self.report["uv_principle"]["selected"]
        self.assertAlmostEqual(sel["delta_phys"], 0.0, places=12)
        self.assertTrue(sel["cp_conserving"])
        self.assertLess(abs(sel["psi_10_minus_Delta"]), 1e-6)
        self.assertGreater(
            self.report["gauge_width_uv_selected"]["tau_e_years"], 0.0
        )
        self.assertTrue(self.report["gauge_width_uv_selected"]["passes_SK"])

    def test_physical_delta_helper(self):
        self.assertAlmostEqual(
            mod.physical_delta(delta_lock=1.0, delta_lam4=0.3), 0.4, places=12
        )
        self.assertTrue(math.isfinite(mod.physical_delta(delta_lock=0.0, delta_lam4=0.0)))


if __name__ == "__main__":
    unittest.main()
