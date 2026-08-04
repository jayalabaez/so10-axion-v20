#!/usr/bin/env python3
"""Tests for charge-allowed potential minimization."""

from __future__ import annotations

import math
import unittest

import charge_allowed_potential_minimize_v20 as mod


class ChargeAllowedMinimizeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()
        cls.fix = cls.report["fixed_couplings"]
        cls.best = cls.report["minimization"]["best"]

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "CHARGE_ALLOWED_POTENTIAL_MINIMIZED__COUPLINGS_CONDITIONAL",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["couplings_minimized_on_reduced_potential"])
        self.assertTrue(flags["soft_mass_shifts_used"])
        self.assertFalse(flags["unique_uv_couplings"])
        self.assertFalse(flags["complete_so10_scalar_potential"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_stationarity_and_hessian(self):
        self.assertTrue(self.best["soft"]["stationarity_restored"])
        self.assertTrue(self.best["radial_hessian_positive_definite"])
        self.assertEqual(self.best["phase_n_positive"], 1)
        self.assertEqual(self.best["phase_n_zero"], 2)

    def test_couplings_finite_perturbative(self):
        for key in ("kappa", "lam4", "lambda_lock"):
            self.assertTrue(math.isfinite(self.fix[key]))
        self.assertTrue(self.best["perturbative"])
        self.assertGreater(abs(self.fix["lambda_lock"]), 0.0)

    def test_finite_kappa_window(self):
        self.assertTrue(self.report["flag"]["finite_kappa_window_demonstrated"])
        fk = self.report["finite_kappa_benchmark_couplings"]
        self.assertIsNotNone(fk)
        self.assertGreaterEqual(abs(fk["kappa"]), 0.05)

    def test_soft_shift_identity_documented(self):
        note = self.report["minimization"]["no_soft_shift_identity"]["note"]
        self.assertIn("κ→0", note)


if __name__ == "__main__":
    unittest.main()
