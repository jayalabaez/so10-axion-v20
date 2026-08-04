#!/usr/bin/env python3
"""Tests for folding Hessian positivity into full-stack τ_p residuals."""

from __future__ import annotations

import unittest

import tau_p_hessian_residual_closure_v20 as mod


class TauPHessianResidualClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "TAU_P_HESSIAN_RESIDUALS_CLOSED__EXACT_UNIQUE_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["hessian_residuals_folded_into_tau_p"])
        self.assertTrue(flags["full_component_hessian_residual_closed"])
        self.assertTrue(flags["tau_p_unique_under_full_uv_stack"])
        self.assertTrue(flags["tau_p_unique_under_hessian_closed_stack"])
        self.assertFalse(flags["live_sarah_or_pyrate_executable_run"])
        self.assertTrue(flags["pq_null_modes_documented_open"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_hessian_residuals_closed(self):
        hess = self.report["certificate"]["hessian_residuals_closed"]
        for name in mod.HESSIAN_RESIDUALS_NOW_CLOSED:
            self.assertTrue(hess[name], msg=name)
        still = self.report["certificate"]["residual_still_open"]
        for name in mod.RESIDUAL_STILL_OPEN:
            self.assertTrue(still[name], msg=name)

    def test_lifetime_positive(self):
        life = self.report["lifetime"]
        self.assertGreater(life["selected_tau_e_years"], 0.0)
        self.assertGreater(life["M_PD_GeV"], 0.0)


if __name__ == "__main__":
    unittest.main()
