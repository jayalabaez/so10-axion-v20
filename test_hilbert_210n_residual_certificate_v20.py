#!/usr/bin/env python3
"""Tests for Hilbert-series 210^n residual-kernel certificate."""

from __future__ import annotations

import unittest

import hilbert_210n_residual_certificate_v20 as mod


class Hilbert210ResidualTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "HILBERT_SERIES_210N_RESIDUAL_KERNEL_CERTIFIED__FLUCTUATION_CG_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["hilbert_series_certificate"])
        self.assertTrue(flags["pure_210_residual_kernel_deg_le_4"])
        self.assertTrue(flags["ps_restriction_injective_deg_2_3_4"])
        self.assertFalse(flags["off_singlet_fluctuation_cg_complete"])
        self.assertFalse(flags["mixed_rep_full_hilbert_series"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_hilbert_coefficients(self):
        coeffs = self.report["hilbert_series"]["coefficients"]
        self.assertEqual(coeffs["2"], 1)
        self.assertEqual(coeffs["3"], 2)
        self.assertEqual(coeffs["4"], 4)

    def test_residual_kernel_vanishes(self):
        res = self.report["residual_off_singlet"]
        self.assertTrue(res["closed"])
        self.assertEqual(res["residual_kernel_total_deg_le_4"], 0)
        for n in ("2", "3", "4"):
            self.assertEqual(res["residual_kernel_by_degree"][n], 0)

    def test_evaluation_ranks(self):
        for n, h in ((2, 1), (3, 2), (4, 4)):
            block = self.report["ps_restriction_ranks"][str(n)]
            self.assertEqual(block["rank"], h)
            self.assertTrue(block["injective_restriction"])


if __name__ == "__main__":
    unittest.main()
