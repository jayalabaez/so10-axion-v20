#!/usr/bin/env python3
"""Tests for residual λ210 / η_intra from the UV PS-singlet potential."""

from __future__ import annotations

import unittest

import residual_lam210_eta_intra_v20 as mod


class ResidualLam210EtaIntraTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "RESIDUAL_LAM210_ETA_INTRA_DERIVED__FULL_210N_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["residual_lam210_eta_intra_derived"])
        self.assertTrue(flags["identified_with_ps_singlet_cubics"])
        self.assertTrue(flags["unique_a_omega_p_vevs_used"])
        self.assertTrue(
            flags["unique_full_triplet_spectrum_under_ps_identification"]
        )
        self.assertFalse(flags["unique_from_full_210n_tensor_basis"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_couplings_and_spectrum(self):
        r = self.report["uv_residual_couplings"]
        self.assertAlmostEqual(r["lam210_10"], r["lam1"])
        self.assertAlmostEqual(r["eta_intra"], r["lam2"])
        self.assertGreater(abs(r["lam210_10"]), 0.0)
        self.assertGreater(abs(r["eta_intra"]), 0.0)
        s = self.report["spectrum_shift"]
        self.assertGreater(s["lightest_closed_GeV"], 0.0)
        self.assertNotAlmostEqual(
            s["lightest_closed_GeV"],
            s["lightest_baseline_GeV"],
            places=3,
        )

    def test_helper(self):
        out = mod.uv_residual_couplings_from_ps_potential(lam1=0.2, lam2=0.3)
        self.assertEqual(out["lam210_10"], 0.2)
        self.assertEqual(out["eta_intra"], 0.3)


if __name__ == "__main__":
    unittest.main()
