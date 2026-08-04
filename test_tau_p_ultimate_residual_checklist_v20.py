#!/usr/bin/env python3
"""Tests for the ultimate τ_p residual checklist."""

from __future__ import annotations

import unittest

import tau_p_ultimate_residual_checklist_v20 as mod


class TauPUltimateResidualChecklistTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "TAU_P_ULTIMATE_RESIDUAL_CHECKLIST_FOLDED__EXACT_UNIQUE_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["ultimate_residual_checklist_folded"])
        self.assertTrue(flags["all_post_hessian_residuals_closed"])
        self.assertTrue(flags["live_sarah_or_pyrate_executable_run"])
        self.assertTrue(flags["scalar_alpha_proven_nonunique_from_flavour"])
        self.assertTrue(flags["cal_G_soft_mode_classified"])
        self.assertTrue(flags["full_quartic_soft_live_dump"])
        self.assertTrue(flags["cal_G_portal_decision_resolved"])
        self.assertTrue(flags["selected_lambda_lock_raised_to_cal_G_lift"])
        self.assertTrue(flags["lam4_potential_raise_proved_spoiling"])
        self.assertFalse(flags["extra_new_portal_required"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_residuals_closed(self):
        closed = self.report["certificate"]["residual_now_closed"]
        for name in mod.RESIDUALS_NOW_CLOSED:
            self.assertTrue(closed[name], msg=name)
        still = self.report["certificate"]["residual_still_open"]
        self.assertNotIn("selected_lambda_lock_below_cal_G_lift_threshold", still)
        self.assertTrue(still["selected_lam4_below_gut_null_tol_threshold"])
        self.assertTrue(still["lam4_cgc_and_dim6_lock_not_in_live_dump"])
        self.assertTrue(still["physical_efjx_cgc_for_210_10_126_S_undetermined"])
        self.assertGreater(
            self.report["certificate"]["c_cgc_needed_abs_approx"], 1.0
        )

    def test_lifetime_positive(self):
        life = self.report["lifetime"]
        self.assertGreater(life["selected_tau_e_years"], 0.0)
        self.assertGreater(life["M_PD_GeV"], 0.0)


if __name__ == "__main__":
    unittest.main()
