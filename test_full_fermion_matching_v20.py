#!/usr/bin/env python3
"""Fail-closed tests for the physical v20 heavy-light current."""

from __future__ import annotations

import math
import unittest

import numpy as np

import full_fermion_matching_v20 as full


class ExactNormalizationTests(unittest.TestCase):
    def test_exact_fa_and_xi(self):
        n = full.exact_normalization()
        self.assertAlmostEqual(n["f_a_GeV"], 3.714032352937078e10, places=3)
        self.assertAlmostEqual(n["xi"], 0.058823529411634885, places=15)

    def test_aligned_benchmark_values(self):
        row = full.coefficients_at_tan_beta(1.5)
        self.assertIn("ALIGNED_CURRENT", row["classification"])
        self.assertAlmostEqual(row["C_e"], 0.04072398190036261, places=14)
        self.assertAlmostEqual(row["C_p_central"], -0.4721493212669636, places=14)
        self.assertAlmostEqual(row["C_n_central"], 0.0065837104071811425, places=14)


class PhysicalPortalCurrentTests(unittest.TestCase):
    @staticmethod
    def simple_block(equal_mixing: bool = False):
        a = np.zeros((2, 5), dtype=complex)
        a[0, 3] = 1.0
        a[1, 4] = 1.0
        b = np.zeros((1, 5), dtype=complex)
        b[0, 0] = 1.0 if equal_mixing else 0.2
        c = np.zeros((2, 1), dtype=complex)
        return a, b, c, 1.0

    def test_projected_plus_berry_identity_but_projected_is_physical(self):
        row = full.portal_current_match(*self.simple_block())
        self.assertLess(row["projected_formula_error"], 1e-12)
        self.assertLess(row["berry_formula_error"], 1e-12)
        self.assertLess(row["moving_identity_error"], 1e-12)
        self.assertGreater(row["projected_shift_norm"], 0.0)
        self.assertGreater(row["berry_norm"], 0.0)

    def test_equal_mixing_counterexample(self):
        row = full.one_family_equal_mixing_counterexample()
        self.assertTrue(row["contains_minus_one_projected_charge"])
        self.assertTrue(row["moving_sum_is_identity"])
        self.assertAlmostEqual(min(row["Q_projected_eigenvalues"]), -1.0)
        self.assertAlmostEqual(max(row["berry_eigenvalues"]), 2.0)

    def test_full_ABCD_scan_detects_portal_dependence_and_fcnc(self):
        scan = full.random_portal_scan(trials=64, seed=20)
        self.assertTrue(scan["passes_fail_closed_detection"])
        self.assertTrue(scan["C_portal_exercised"])
        self.assertGreater(scan["largest_projected_current_shift"], 0.1)
        self.assertGreater(scan["largest_random_mass_basis_offdiagonal"], 1e-3)
        self.assertLess(scan["worst_moving_identity_error"], 1e-8)

    def test_schur_rank_and_heavy_mass_fail_closed(self):
        a = np.zeros((2, 5), dtype=complex)
        b = np.zeros((1, 5), dtype=complex)
        c = np.zeros((2, 1), dtype=complex)
        with self.assertRaises(ValueError):
            full.portal_current_match(a, b, c, 1.0)
        a[0, 3] = 1.0
        a[1, 4] = 1.0
        with self.assertRaises(ValueError):
            full.portal_current_match(a, b, c, 0.0)

    def test_physical_pq_plus_gauge_basis_does_not_remove_dependence(self):
        a, b, c, d = self.simple_block()
        c_phys = -16.0 * full.VS_GEV**2 / full.NORMALIZATION["D_GeV"] ** 2
        row = full.portal_current_match(
            a, b, c, d, gauge_admixture=c_phys
        )
        self.assertLess(row["moving_identity_error"], 1e-12)
        self.assertGreater(row["projected_shift_norm"], 0.0)


class ScientificStatusTests(unittest.TestCase):
    def test_report_keeps_full_matching_open(self):
        report = full.build_report()
        self.assertEqual(report["n_failed"], 0)
        self.assertIn("MATCHING_OPEN", report["status"])
        self.assertTrue(report["full_model_status"]["portal_matrices_required"])
        self.assertFalse(
            report["full_model_status"]["tree_FCNC_absence_proved"]
        )
        self.assertFalse(
            report["full_model_status"]["unique_symbolic_full_model_Ce_Cp_Cn"]
        )
        self.assertIsNone(
            report["full_model_status"]["full_model_stellar_SN_pass"]
        )

    def test_invalid_beta_rejected(self):
        for value in (0.0, -1.0, float("inf"), float("nan")):
            with self.assertRaises(ValueError):
                full.coefficients_at_tan_beta(value)


if __name__ == "__main__":
    unittest.main()
