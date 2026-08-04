#!/usr/bin/env python3
"""Tests for the cal G portal decision certificate."""

from __future__ import annotations

import unittest

import cal_g_portal_decision_v20 as mod


class CalGPortalDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_ok(self):
        self.assertEqual(self.report["n_failed"], 0)
        self.assertEqual(
            self.report["status"], "CAL_G_PORTAL_DECISION_RESOLVED__TAU_P_OPEN"
        )

    def test_decision_no_extra_new_portal(self):
        dec = self.report["decision"]
        flags = self.report["flag"]
        self.assertFalse(dec["extra_new_portal_required"])
        self.assertFalse(flags["extra_new_portal_required"])
        self.assertTrue(dec["existing_lambda_lock_sufficient_in_principle"])
        self.assertIn(
            dec["label"],
            {
                "existing_lambda_lock_clears_at_selected",
                "existing_lambda_lock_sufficient_after_O1_raise",
            },
        )

    def test_soft_mode_orthogonal(self):
        soft = self.report["soft_mode"]
        self.assertEqual(soft["classification_label"], "residual_flat_or_light_singlet")
        self.assertLess(soft["overlap_goldstone_dir"], 0.5)
        self.assertGreaterEqual(soft["overlap_orthogonal_dir"], 0.5)

    def test_mu_crit_and_lock(self):
        dec = self.report["decision"]
        self.assertGreater(dec["mu_crit_GeV"], 0.0)
        self.assertGreater(dec["lambda_lock_crit_abs"], 0.0)
        lock = self.report["portals"]["lambda_lock"]
        self.assertTrue(lock["perturbative_O1_window"])
        # Crit embedding should clear null tol
        self.assertTrue(self.report["embeddings"]["at_lambda_lock_crit"]["above_null_tol"])
        self.assertTrue(
            self.report["embeddings"]["at_lambda_lock_crit"]["chiral_5x5_null_ok"]
        )

    def test_lam4_not_overclaimed(self):
        self.assertFalse(
            self.report["portals"]["lam4"]["can_lift_cal_G_orth_inside_eq102"]
        )
        self.assertFalse(self.report["flag"]["exact_unique_proton_lifetime"])
        self.assertFalse(self.report["flag"]["whole_model_excluded"])

    def test_lock_mass_helpers(self):
        m_i, m_gut = 1e12, 1e16
        mu = mod.lambda_lock_soft_mass_GeV(2.0, m_i=m_i, m_gut=m_gut)
        ll = mod.lambda_lock_for_soft_mass(mu, m_i=m_i, m_gut=m_gut)
        self.assertAlmostEqual(ll, 2.0, places=9)


if __name__ == "__main__":
    unittest.main()
