#!/usr/bin/env python3
"""Tests for charge-allowed nonsusy M_T builder."""

from __future__ import annotations

import unittest

import nonsusy_charge_allowed_mt_v20 as mod


class ChargeAllowedMTTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "NONSUSY_CHARGE_ALLOWED_MT_BUILT__CG_NORMALIZATIONS_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["charge_allowed_mt_built"])
        self.assertTrue(flags["bare_10_squared_absent"])
        self.assertTrue(flags["ten2_S_mixing_included"])
        self.assertTrue(flags["locking_phase_hessian_computed"])
        self.assertFalse(flags["complete_phase_hessian"])
        self.assertFalse(flags["invented_unpublished_cg_normalizations"])
        self.assertFalse(flags["complete_so10_scalar_potential"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_mix_off_zero_offdiag(self):
        m = mod.fill_charge_allowed_mt(
            v210=1e16,
            vS=1e12,
            mu10=1e12,
            mu126=1e12,
            lam210_10=0.0,
            lam210_126=0.0,
            lamS_10=0.0,
            lamS_126=0.0,
            lam_mix=5.0,
            include_conditional_mix=False,
        )
        self.assertEqual(m[0, 1], 0.0)

    def test_phase_hessian_spectrum(self):
        ph = self.report["locking_phase_hessian"]
        self.assertEqual(ph["n_positive"], 1)
        self.assertEqual(ph["n_zero"], 2)

    def test_ledger_excludes_bare10(self):
        self.assertTrue(self.report["operator_ledger"]["bare_10_squared_excluded"])
        self.assertTrue(self.report["operator_ledger"]["ten2_S_included"])

    def test_scenarios_mixed(self):
        self.assertGreater(self.report["n_excluded_by_ps_mu_K0"], 0)
        self.assertLess(
            self.report["n_excluded_by_ps_mu_K0"], self.report["n_scenarios"]
        )


if __name__ == "__main__":
    unittest.main()
