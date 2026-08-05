#!/usr/bin/env python3
"""Tests for OPEN_MIXED_126 PS-singlet Sigmabar M² fill."""

from __future__ import annotations

import unittest

import diagonal_sigmabar_m2_mixed_126_ps_singlet_v20 as mod


class Mixed126PSSingletTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "OPEN_MIXED_126_PS_SINGLET_PARTIAL_M2_FILLED__FULL_CG_OPEN",
        )
        flags = self.report["flags"]
        self.assertTrue(flags["OPEN_MIXED_126_ps_singlet_partial_filled"])
        self.assertTrue(flags["positive_hermitian_schur_C_seed_from_mixed_126"])
        self.assertFalse(flags["full_tensor_CG_normalized"])
        self.assertFalse(flags["invented_missing_cg"])
        self.assertFalse(flags["full_component_hessian_complete"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_seed_and_slot(self):
        seed = self.report["seed"]
        self.assertGreater(seed["eff_210_for_126_GeV"], 0.0)
        self.assertGreater(seed["delta_M2_GeV2"], 0.0)
        self.assertFalse(seed["full_tensor_normalized"])
        slot = self.report["slot_fill"]["OPEN_MIXED_126"]
        self.assertEqual(slot["status"], "PARTIAL_PS_SINGLET_M2_FILLED")
        self.assertTrue(slot["positive_hermitian_schur_seed"])
        self.assertEqual(len(self.report["C_partial_from_mixed_126_GeV2"]), 126)
        self.assertTrue(self.report["still_open"]["OPEN_MIXED_120"])
        self.assertTrue(self.report["still_open"]["OPEN_MIXED_320"])

    def test_helper(self):
        seed = mod.mixed_126_mass2_seed(
            a=0.3e16, p=0.2e16, omega=0.5e16, m_gut=1.0e16, lam_tilde=0.01
        )
        self.assertAlmostEqual(
            seed["eff_210_for_126_GeV"], abs(0.5e16 + 0.3e16) + abs(0.2e16), places=6
        )
        self.assertGreater(seed["delta_M2_GeV2"], 0.0)


if __name__ == "__main__":
    unittest.main()
