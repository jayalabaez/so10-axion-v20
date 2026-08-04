#!/usr/bin/env python3
"""Tests for reduced-sector two-loop quartic / soft β ingest."""

from __future__ import annotations

import math
import unittest

import quartic_soft_betas_v20 as mod


class QuarticSoftBetasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "QUARTIC_SOFT_BETAS_INGESTED__FULL_210N_AND_UNIQUE_TAU_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["two_loop_quartic_betas_complete"])
        self.assertTrue(flags["pyrate_sarah_quartic_soft_formulas_ingested"])
        self.assertTrue(flags["reduced_charge_allowed_sector_only"])
        self.assertTrue(flags["residual_casimir_zero_after_so10_breaking"])
        self.assertTrue(flags["soft_m2_betas_included"])
        self.assertTrue(flags["portal_kappa_lam4_lock_betas_included"])
        self.assertFalse(flags["live_sarah_or_pyrate_executable_run"])
        self.assertFalse(flags["full_210n_tensor_betas"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_ledger_and_evolution(self):
        gut = self.report["boundary_GUT"]
        self.assertEqual(gut["ledger"]["n_couplings"], 8)
        self.assertFalse(gut["ledger"]["use_parent_casimir"])
        warn = gut["parent_casimir_warning"]
        self.assertGreater(warn["max_abs_beta_total"], 0.0)
        self.assertTrue(warn["ledger"]["use_parent_casimir"])
        evo = self.report["evolution_GUT_to_MI"]
        self.assertTrue(evo["success"])
        self.assertTrue(evo["all_quartics_positive"])
        self.assertTrue(math.isfinite(evo["max_abs_rel_shift_lambda"]))
        self.assertGreater(evo["max_abs_rel_shift_lambda"], 0.0)
        for name, val in evo["lambdas_end"].items():
            self.assertGreater(val, 0.0, msg=name)
        mi = self.report["boundary_MI"]
        self.assertEqual(set(mi["lambdas"]), set(gut["lambdas"]))
        self.assertEqual(set(mi["portals"]), set(gut["portals"]))

    def test_beta_helpers_finite(self):
        b1 = mod.beta_lambda_one_loop(0.5, g=0.7, c2=2.0)
        b2 = mod.beta_lambda_two_loop(0.5, g=0.7, c2=2.0)
        self.assertTrue(math.isfinite(b1 + b2))
        bm = mod.beta_m2_one_loop(1e20, 0.5, g=0.7, c2=2.0)
        self.assertTrue(math.isfinite(bm))


if __name__ == "__main__":
    unittest.main()
