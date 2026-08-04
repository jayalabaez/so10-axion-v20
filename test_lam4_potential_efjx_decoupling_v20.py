#!/usr/bin/env python3
"""Tests for λ₄-potential / E/F/J/X decoupling certificate."""

from __future__ import annotations

import unittest

import lam4_potential_efjx_decoupling_v20 as mod


class Lam4PotentialEfjxDecouplingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_ok(self):
        self.assertEqual(self.report["n_failed"], 0)
        self.assertEqual(
            self.report["status"],
            "LAM4_POTENTIAL_EFJX_DECOUPLING_PROVED__TAU_P_OPEN",
        )

    def test_raise_spoils_and_cgc_needed(self):
        flags = self.report["flag"]
        self.assertTrue(flags["lam4_potential_raise_proved_spoiling"])
        self.assertTrue(flags["gamma_eff_decoupled_from_lam4_potential"])
        self.assertTrue(flags["cgc_ratio_needed_quantified"])
        c = self.report["couplings"]
        self.assertGreater(c["raise_factor"], 1.0)
        self.assertGreater(c["c_cgc_needed_abs_approx"], 1.0)
        self.assertFalse(
            self.report["spoilage"]["at_raised_lam4_potential"][
                "radial_hessian_positive_definite"
            ]
        )

    def test_gamma_crit_clears_efjx(self):
        efjx = self.report["efjx"]["at_gamma_crit_lam4_potential_fixed"]
        self.assertTrue(efjx["clears_gut_null_tol"])
        self.assertEqual(efjx["efjx_n_null_below_tol"], 0)

    def test_honesty(self):
        flags = self.report["flag"]
        self.assertTrue(flags["selected_lam4_still_below_gut_null_tol"])
        self.assertTrue(flags["lam4_cgc_and_dim6_lock_not_in_live_dump"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_raised_helper(self):
        out = mod.raised_lam4(-3.18e-6, 6.06e-4)
        self.assertLess(out["lam4_potential_raised"], 0.0)
        self.assertGreaterEqual(abs(out["lam4_potential_raised"]), 6.06e-4)


if __name__ == "__main__":
    unittest.main()
