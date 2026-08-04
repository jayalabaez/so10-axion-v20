#!/usr/bin/env python3
"""Tests for PQ-null lift via the λ₄ portal."""

from __future__ import annotations

import unittest

import pq_null_lam4_portal_lift_v20 as mod


class PQNullLam4PortalLiftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "PQ_NULL_EXACT_KERNEL_LIFTED_BY_LAM4__LIGHT_MASSES_DOCUMENTED",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["pq_null_exact_kernel_lifted_by_lam4"])
        self.assertTrue(flags["lam4_portal_charge_allowed"])
        self.assertTrue(flags["bare_gamma_pq_forbidden"])
        self.assertFalse(flags["selected_lam4_clears_gut_null_tol"])
        self.assertTrue(flags["cal_G_soft_mode_documented"])
        self.assertFalse(flags["live_sarah_or_pyrate_executable_run"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_baseline_vs_lifted(self):
        base = self.report["baseline_gamma0"]
        lift = self.report["lifted_selected_lam4"]
        self.assertEqual(base["efjx_exact_algebraic_nulls"], 4)
        self.assertEqual(lift["efjx_exact_algebraic_nulls"], 0)
        for name in mod.EFJX:
            self.assertEqual(base["efjx_min_GeV"][name], 0.0)
            self.assertGreater(lift["efjx_min_GeV"][name], 0.0)

    def test_portal_charges(self):
        portal = mod.lam4_portal_charge_certificate()
        self.assertTrue(portal["allowed"]["all"])
        self.assertEqual(portal["charge_totals"]["PQ"], 0)
        self.assertFalse(portal["bare_gamma_Phi_H_Sigma"]["allowed"]["PQ"])

    def test_critical_lam4(self):
        crit = self.report["critical_lam4"]
        self.assertTrue(crit["found"])
        self.assertGreater(crit["lam4_crit_abs"], abs(self.report["matching"]["lam4_selected"]))


if __name__ == "__main__":
    unittest.main()
