#!/usr/bin/env python3
"""Tests for the signed non-SUSY triplet mass-squared proxy."""
from __future__ import annotations

import unittest

import numpy as np

import nonsusy_charge_allowed_mt_v20 as mod


class SignedMT2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "NONSUSY_SIGNED_MT2_PROXY_BUILT__FULL_COMPONENT_CG_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        flags = self.report["flag"]
        self.assertTrue(flags["charge_and_so10_allowed_mt2_proxy_built"])
        self.assertTrue(flags["mass_squared_matrix_used"])
        self.assertTrue(flags["forbidden_210_10dag10_absent"])
        self.assertTrue(flags["forbidden_10_126_S_absent"])
        self.assertTrue(flags["lambda4_offdiag_slot_included"])
        self.assertTrue(flags["bare_10_squared_absent"])
        self.assertTrue(flags["ten2_S_mixing_included"])
        self.assertTrue(flags["locking_phase_hessian_computed"])
        self.assertFalse(flags["complete_phase_hessian"])
        self.assertFalse(flags["physical_component_CG_complete"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_forbidden_inputs_are_ignored(self):
        common = dict(
            v210=1e16,
            vS=1e12,
            mu10=1e12,
            mu126=1e12,
            lam210_126=0.0,
            lamS_10=0.0,
            lamS_126=0.0,
            lam2102_10=0.0,
            lam4_cg=0.0,
        )
        baseline = mod.fill_charge_allowed_mt(
            **common,
            lam210_10=0.0,
            lam_mix=0.0,
            include_conditional_mix=False,
        )
        forbidden = mod.fill_charge_allowed_mt(
            **common,
            lam210_10=99.0,
            lam_mix=99.0,
            include_conditional_mix=True,
        )
        self.assertTrue(np.array_equal(baseline, forbidden))
        self.assertEqual(forbidden[0, 1], 0.0)

    def test_allowed_quartic_and_lambda4_slots(self):
        matrix = mod.fill_charge_allowed_mt(
            v210=1e16,
            vS=1e12,
            mu10=0.0,
            mu126=1e12,
            lam210_10=123.0,
            lam210_126=0.0,
            lamS_10=0.0,
            lamS_126=0.0,
            lam_mix=456.0,
            include_conditional_mix=True,
            lam2102_10=0.5,
            lam4_cg=1e-4,
        )
        self.assertAlmostEqual(matrix[0, 0], 0.5e32)
        self.assertAlmostEqual(matrix[0, 1], 1e24)
        self.assertAlmostEqual(matrix[1, 0], 1e24)

    def test_phase_hessian_spectrum(self):
        phase = self.report["locking_phase_hessian"]
        self.assertEqual(phase["n_positive"], 1)
        self.assertEqual(phase["n_zero"], 2)

    def test_ledger_signed_scope(self):
        ledger = self.report["operator_ledger"]
        self.assertTrue(ledger["bare_10_squared_excluded"])
        self.assertTrue(ledger["forbidden_210_10dag10_excluded"])
        self.assertTrue(ledger["forbidden_10_126_S_excluded"])
        self.assertTrue(ledger["ten2_S_included"])
        self.assertTrue(ledger["quartic_2102_10dag10_included"])
        self.assertTrue(ledger["lambda4_210_10_126_S_included"])

    def test_scenarios_include_survival_and_conditional_failure(self):
        self.assertGreater(self.report["n_excluded_by_ps_mu_K0"], 0)
        self.assertLess(
            self.report["n_excluded_by_ps_mu_K0"], self.report["n_scenarios"]
        )
        rows = self.report["scenarios"]
        self.assertTrue(all(row["flag"]["mass_squared_matrix_used"] for row in rows))
        self.assertTrue(all(not row["flag"]["physical_triplet_spectrum_complete"] for row in rows))


if __name__ == "__main__":
    unittest.main()
