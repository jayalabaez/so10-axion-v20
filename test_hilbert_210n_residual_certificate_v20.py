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
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        flags = self.report["flag"]
        self.assertTrue(flags["hilbert_series_certificate"])
        self.assertTrue(flags["pure_210_residual_kernel_deg_le_4"])
        self.assertTrue(flags["ps_restriction_injective_deg_2_3_4"])
        self.assertTrue(flags["legacy_two_cubic_basis_withdrawn"])
        self.assertTrue(flags["mixed_rep_multiplicities_exact"])
        self.assertFalse(flags["off_singlet_fluctuation_cg_complete"])
        self.assertFalse(flags["mixed_rep_full_hilbert_series"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_hilbert_coefficients_are_the_exact_census(self):
        coeffs = self.report["hilbert_series"]["coefficients"]
        self.assertEqual(coeffs["2"], 1)
        self.assertEqual(coeffs["3"], 1)
        self.assertEqual(coeffs["4"], 4)
        self.assertEqual(coeffs, self.report["hilbert_series"]["exact_census"])

    def test_residual_kernel_vanishes(self):
        res = self.report["residual_off_singlet"]
        self.assertTrue(res["closed"])
        self.assertEqual(res["residual_kernel_total_deg_le_4"], 0)
        for n in ("2", "3", "4"):
            self.assertEqual(res["residual_kernel_by_degree"][n], 0)

    def test_evaluation_ranks(self):
        for n, h in ((2, 1), (3, 1), (4, 4)):
            block = self.report["ps_restriction_ranks"][str(n)]
            self.assertEqual(block["rank"], h)
            self.assertTrue(block["injective_restriction"])

    def test_images_are_the_genuine_so10_invariants(self):
        audit = self.report["ps_singlet_images"]["max_deviation_from_exact_tensors"]
        self.assertLess(audit["I2"], 1.0e-12)
        self.assertLess(audit["I3"], 1.0e-12)
        self.assertLess(audit["J"], 1.0e-9)
        self.assertLess(self.report["ps_singlet_images"]["msgut_cubic_max_residual"], 1.0e-12)

    def test_withdrawn_two_cubic_basis_cannot_represent_the_cubic(self):
        correction = self.report["source_correction"]
        self.assertEqual(correction["old_H3"], 2)
        self.assertEqual(correction["correct_H3"], 1)
        fit = correction["legacy_fit_of_genuine_cubic"]
        self.assertFalse(fit["genuine_cubic_in_legacy_span"])
        self.assertGreater(fit["relative_residual"], 0.1)
        self.assertEqual(len(mod.ps_forms_degree3(0.3, 1.2, -0.7)), 1)

    def test_mixed_multiplicities_are_exact(self):
        counts = {
            entry["operator"]: entry["singlet_multiplicity"]
            for entry in self.report["mixed_rep"]["entries"]
        }
        self.assertEqual(counts["210 · 10† · 10"], 0)
        self.assertEqual(counts["210 · 10† · 126bar"], 1)
        self.assertEqual(counts["210 · 126† · 126"], 1)
        self.assertEqual(counts["210 · 10 · 126 · S"], 1)
        control = self.report["mixed_rep"]["control_decompositions"]
        self.assertEqual(control["10x10_contains_210"], 0)
        self.assertEqual(control["210x210_contains_1"], 1)


if __name__ == "__main__":
    unittest.main()
