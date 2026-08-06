#!/usr/bin/env python3
from __future__ import annotations

import unittest

import numpy as np

import exact_10h_holomorphic_quartic_triplet_v20 as exact


class Exact10HHolomorphicQuarticTripletTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = exact.build_report()

    def test_gate_closes_projection(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "CLOSED_SUBPROBLEM")

    def test_coordinate_bilinear(self) -> None:
        plus = np.array([0, 0, 0, 0.6 + 0.1j, -0.2 + 0.3j], dtype=complex)
        minus = np.array([0, 0, 0, 0.4 - 0.2j, 0.5 + 0.1j], dtype=complex)
        self.assertAlmostEqual(
            exact.holomorphic_bilinear_from_coordinates(plus, minus).real,
            exact.analytic_holomorphic_bilinear(plus, minus).real,
            places=12,
        )
        self.assertAlmostEqual(
            exact.holomorphic_bilinear_from_coordinates(plus, minus).imag,
            exact.analytic_holomorphic_bilinear(plus, minus).imag,
            places=12,
        )

    def test_exact_bterm_formula(self) -> None:
        coupling = 0.3
        q0 = 2.0 + 4.0j
        expected = 2.0 * coupling * np.conjugate(q0)
        self.assertEqual(exact.triplet_bterm_m2(coupling, q0), expected)

    def test_no_hermitian_diagonal_and_color_degeneracy(self) -> None:
        result = self.report["exact_result"]
        self.assertEqual(result["Hermitian_diagonal_shift_from_this_channel"], 0.0)
        self.assertTrue(result["same_for_each_color_weight"])
        benchmark = self.report["benchmark"]
        self.assertLess(benchmark["extraction_residual"], 1e-6)
        self.assertLess(max(benchmark["single_field_diagonal_residuals"]), 1e-10)
        coeffs = benchmark["real_equal_perturbation_coefficients"]
        self.assertLess(max(coeffs) - min(coeffs), 1e-10)

    def test_scope_and_dimensions(self) -> None:
        dimensions = self.report["dimensional_contract"]
        self.assertEqual(dimensions["lambda10_hol"], "dimensionless")
        self.assertEqual(dimensions["Q_H0"], "GeV^2")
        self.assertEqual(dimensions["Delta_B"], "GeV^2")
        flags = self.report["flag"]
        self.assertTrue(flags["exact_10h_holomorphic_quartic_triplet_projection"])
        self.assertTrue(flags["exact_B_correction_formula_derived"])
        self.assertFalse(flags["physical_Q_H0_derived"])
        self.assertFalse(flags["complete_component_potential"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
