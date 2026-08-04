#!/usr/bin/env python3
"""Tests for transcribed literature CG triplet mass matrices."""

from __future__ import annotations

import unittest

import numpy as np

import literature_cg_triplet_matrix_v20 as mod


class LiteratureCGTripletTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_honesty_flags(self):
        self.assertEqual(
            self.report["status"],
            "LITERATURE_CG_TRIPLET_MATRICES_TRANSCRIBED__NONSUSY_POTENTIAL_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["literature_cg_transcribed"])
        self.assertTrue(flags["aulakh_cal_T_implemented"])
        self.assertTrue(flags["fukuyama_su5_M_triplet_implemented"])
        self.assertFalse(flags["invented_unpublished_tensors"])
        self.assertFalse(flags["identified_with_v20_nonsusy_potential"])
        self.assertFalse(flags["complete_so10_scalar_potential"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_aulakh_T_entry_transcription(self):
        T = mod.aulakh_cal_T(
            M_H=7.0,
            M=3.0,
            m=1.0,
            lam=1.0,
            eta=1.0,
            gamma=1.0,
            gamma_bar=2.0,
            a=0.1,
            p=0.2,
            omega=0.3,
            sigma=0.01,
            sigma_bar=0.02,
        )
        self.assertAlmostEqual(T[0, 0], 7.0)
        self.assertAlmostEqual(T[1, 2], 3.0)
        self.assertAlmostEqual(T[0, 1], 2.0 * (0.1 + 0.2))

    def test_fukuyama_definitions(self):
        Mt = mod.fukuyama_su5_M_triplet(
            m1=1.0, m2=2.0, m3=3.0, lam1=0.1, lam2=1.0, lam3=0.2, lam4=0.3
        )
        self.assertEqual(Mt.shape, (5, 5))
        self.assertAlmostEqual(Mt[0, 0], 6.0)  # 2*m3
        self.assertAlmostEqual(Mt[2, 2], 2.0)  # m2

    def test_svd_spectrum_positive(self):
        T = mod.aulakh_cal_T(
            M_H=1e16,
            M=1e16,
            m=1e16,
            lam=1.0,
            eta=1.0,
            gamma=1.0,
            gamma_bar=1.0,
            a=3e15,
            p=2e15,
            omega=5e15,
            sigma=6e11,
            sigma_bar=6e11,
        )
        spec = mod.physical_spectrum(T)
        self.assertTrue(spec["positive_spectrum"])
        self.assertEqual(spec["n_modes"], 5)

    def test_scenarios_mixed_exclusion(self):
        self.assertGreater(self.report["n_scenarios"], 0)
        self.assertLess(
            self.report["n_excluded_by_ps_mu_K0"], self.report["n_scenarios"]
        )


if __name__ == "__main__":
    unittest.main()
