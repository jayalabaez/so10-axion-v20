#!/usr/bin/env python3
"""Tests for mixed 210–126–10 masses at Hilbert VEVs."""

from __future__ import annotations

import unittest

import mixed_210_126_10_hilbert_hessian_v20 as mod


class Mixed21012610HilbertHessianTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "MIXED_210_126_10_COMPLETE_AT_HILBERT__PQ_NULLS_DOCUMENTED",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["mixed_210_126_10_complete"])
        self.assertTrue(flags["mixed_evaluated_at_hilbert_vevs"])
        self.assertTrue(flags["cal_T_D_E_F_J_X_G_included"])
        self.assertTrue(flags["pq_gamma_set_to_zero"])
        self.assertTrue(flags["pq_null_modes_documented"])
        self.assertTrue(flags["combined_extended_hessian_pd"])
        self.assertFalse(flags["live_sarah_or_pyrate_executable_run"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_spectra(self):
        sp = self.report["mixed_spectra"]
        self.assertEqual(sp["n_blocks"], 7)
        self.assertTrue(sp["all_physical_positive"])
        self.assertGreaterEqual(sp["n_pq_null_modes"], 1)
        self.assertGreater(sp["n_physical_modes"], 0)
        self.assertGreater(sp["lightest_GeV"], 0.0)

    def test_helper_params(self):
        p = mod.hilbert_matched_params(
            a=1.0, omega=1.0, p=1.0, m_i=1.0, m_gut=1.0, lam=0.1, eta=0.1
        )
        self.assertEqual(p["gamma"], 0.0)
        self.assertTrue(p["pq_gamma_forbidden"])


if __name__ == "__main__":
    unittest.main()
