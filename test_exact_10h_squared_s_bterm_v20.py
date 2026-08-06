#!/usr/bin/env python3
from __future__ import annotations

import unittest

import numpy as np

import exact_10h_squared_s_bterm_v20 as exact


class Exact10HSquaredSBTermTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = exact.build_report()

    def test_gate_closes_subproblem(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "CLOSED_SUBPROBLEM")

    def test_canonical_kinetic_and_symmetric_bilinear(self) -> None:
        gram = exact.kinetic_gram()
        q = exact.bilinear_matrix()
        expected = np.block(
            [
                [np.zeros((5, 5)), np.eye(5)],
                [np.eye(5), np.zeros((5, 5))],
            ]
        )
        self.assertLess(float(np.max(np.abs(gram - np.eye(10)))), 1e-12)
        self.assertLess(float(np.max(np.abs(q - expected))), 1e-12)

    def test_each_complex_pair_has_factor_two(self) -> None:
        for index in range(5):
            self.assertAlmostEqual(exact.expansion_coefficient(index), 2.0, places=12)
        with self.assertRaises(ValueError):
            exact.expansion_coefficient(5)

    def test_so10_invariance(self) -> None:
        self.assertLess(exact.generator_invariance_residual(), 1e-12)

    def test_exact_triplet_bterm(self) -> None:
        self.assertEqual(exact.bterm_m2(3.0, 5.0), 15.0 + 0.0j)
        triplet = self.report["triplet_result"]
        self.assertEqual(triplet["coefficient"], 1.0)
        self.assertTrue(triplet["same_for_each_color_weight"])

    def test_dimension_and_claim_scope(self) -> None:
        dimensions = self.report["dimensional_contract"]
        self.assertEqual(dimensions["kappa10"], "GeV")
        self.assertEqual(dimensions["S_expectation"], "GeV")
        self.assertEqual(dimensions["B_entry"], "GeV^2")
        flags = self.report["flag"]
        self.assertTrue(flags["exact_10h_squared_s_normalization_derived"])
        self.assertTrue(flags["exact_triplet_B_coefficient_derived"])
        self.assertTrue(flags["normalization_guess_removed"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
