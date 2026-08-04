#!/usr/bin/env python3
"""Tests for two-loop matrix flavour RG with PS thresholds."""

from __future__ import annotations

import unittest

import two_loop_matrix_flavour_rg_ps_v20 as mod


class TwoLoopMatrixFlavourRGTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "TWO_LOOP_MATRIX_FLAVOUR_RG_PS_THRESHOLDS_IN_GAUGE_WIDTH__"
            "SARAH_SO10_210_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["two_loop_matrix_flavour_rge"])
        self.assertTrue(flags["ps_threshold_matching_in_chain"])
        self.assertTrue(flags["gauge_width_uses_matrix_GUT_ckm"])
        self.assertFalse(flags["two_loop_so10_complete"])
        self.assertFalse(flags["sarah_validated_210_betas"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_gauge_width(self):
        g = self.report["gauge_width"]
        self.assertTrue(g["passes_SK_e_pi0"])
        self.assertGreater(g["F_e_matrix_GUT"], 0.0)
        self.assertTrue(abs(g["delta_rel_tau_vs_wolfenstein"]) < 1.0)


if __name__ == "__main__":
    unittest.main()
