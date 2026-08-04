#!/usr/bin/env python3
"""Tests for raising |λ_lock| to the cal G lift threshold."""

from __future__ import annotations

import unittest

import lambda_lock_cal_g_lift_v20 as mod


class LambdaLockCalGLiftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_ok(self):
        self.assertEqual(self.report["n_failed"], 0)
        self.assertEqual(
            self.report["status"], "LAMBDA_LOCK_CAL_G_LIFT_EXECUTED__TAU_P_OPEN"
        )

    def test_raise_and_clear(self):
        c = self.report["couplings"]
        self.assertGreaterEqual(
            abs(c["lambda_lock_raised"]), c["lambda_lock_crit_abs"]
        )
        self.assertGreater(c["raise_factor"], 1.0)
        flags = self.report["flag"]
        self.assertTrue(flags["selected_lambda_lock_raised_to_cal_G_lift"])
        self.assertTrue(flags["cal_G_soft_mode_cleared_at_raised_lock"])
        self.assertTrue(flags["selected_point_not_spoiled_by_lock_raise"])

    def test_cal_g_spectrum(self):
        raised = self.report["cal_G"]["at_raised_lambda_lock"]
        self.assertTrue(raised["clears_null_tol"])
        self.assertTrue(raised["with_lambda_lock_embed"]["above_null_tol"])
        self.assertTrue(raised["with_lambda_lock_embed"]["chiral_5x5_null_ok"])
        # Selected embed should still be soft ( motivating the raise )
        sel = self.report["cal_G"]["at_selected_lambda_lock"]
        self.assertFalse(sel["clears_null_tol"])

    def test_kappa_lam4_fixed_honesty(self):
        c = self.report["couplings"]
        self.assertAlmostEqual(abs(c["kappa_fixed"]), abs(c["kappa_fixed"]))
        self.assertFalse(self.report["flag"]["exact_unique_proton_lifetime"])
        self.assertFalse(self.report["flag"]["whole_model_excluded"])
        self.assertTrue(self.report["flag"]["selected_lam4_still_below_gut_null_tol"])

    def test_raised_helper(self):
        out = mod.raised_lambda_lock(0.955, 2.5889)
        self.assertGreater(abs(out["lambda_lock_raised"]), 2.5889)
        self.assertAlmostEqual(out["raise_factor"], abs(out["lambda_lock_raised"]) / 0.955)


if __name__ == "__main__":
    unittest.main()
