#!/usr/bin/env python3
import unittest

import numpy as np

import pure_210_ps_singlet_quartic_polynomials_v20 as poly


class Pure210PSSingletQuarticPolynomialTests(unittest.TestCase):
    def test_analytic_matches_direct(self):
        rng = np.random.default_rng(2104)
        for _ in range(12):
            point = rng.normal(size=3)
            analytic = poly.analytic_invariants(*point)
            direct = poly.direct_invariants(*point)
            for name in analytic:
                self.assertAlmostEqual(analytic[name], direct[name], places=10)

    def test_channel_norms_are_nonnegative(self):
        rng = np.random.default_rng(45)
        for _ in range(100):
            inv = poly.analytic_invariants(*rng.normal(size=3))
            for name, value in inv.items():
                self.assertGreaterEqual(value, -1e-14, (name, value))

    def test_potential_identity(self):
        rng = np.random.default_rng(1050)
        for _ in range(20):
            point = rng.normal(size=3)
            couplings = rng.normal(size=4)
            left = poly.original_basis_potential(
                *point,
                g45=couplings[0],
                g210=couplings[1],
                g1050=couplings[2],
                lam=couplings[3],
            )
            right = poly.identity_reduced_potential(
                *point,
                g45=couplings[0],
                g210=couplings[1],
                g1050=couplings[2],
                lam=couplings[3],
            )
            self.assertAlmostEqual(left, right, places=10)

    def test_four_invariants_are_independent(self):
        matrix = poly.invariant_evaluation_matrix()
        self.assertEqual(np.linalg.matrix_rank(matrix, tol=1e-12), 4)
        self.assertGreater(abs(np.linalg.det(matrix)), 1e-12)

    def test_report_scope(self):
        report = poly.build_report()
        self.assertEqual(report["n_failed"], 0, report)
        self.assertEqual(report["overall_state"], "BLOCKED")
        self.assertTrue(report["closure"]["pure_210_ps_singlet_quartic_polynomials_closed"])
        self.assertTrue(report["flags"]["manifest_sum_of_squares_certificate"])
        self.assertFalse(report["closure"]["mixed_field_invariant_ring_G1_closed"])
        self.assertFalse(report["flags"]["whole_model_validated"])


if __name__ == "__main__":
    unittest.main()
