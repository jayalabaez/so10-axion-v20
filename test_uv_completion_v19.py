#!/usr/bin/env python3
"""Independent regressions for the anomaly-free U(1)_X completion."""

from __future__ import annotations

from collections import Counter
import math
import unittest

import numpy as np

import spin10_referee_audit as spin10
import uv_completion_v19 as uv


class ContinuousAnomalyTests(unittest.TestCase):
    def test_anomalies_cancel_by_direct_integer_arithmetic(self):
        light = (
            3 * 2 * 1 + 5 * 2 * (2 - 6),
            3 * 16 * 1 + 5 * 16 * (2 - 6),
            3 * 16 * 1**3 + 5 * 16 * (2**3 + (-6) ** 3),
        )
        spin = (2 * (7 + 10), 16 * (7 + 10), 16 * (7**3 + 10**3))
        singlets = (0, sum((-6, 23, -26, 9)), sum(q**3 for q in (-6, 23, -26, 9)))
        self.assertEqual(light, (-34, -272, -16592))
        self.assertEqual(spin, (34, 272, 21488))
        self.assertEqual(singlets, (0, 0, -4896))
        self.assertEqual(tuple(sum(row[i] for row in (light, spin, singlets)) for i in range(3)), (0, 0, 0))

    def test_all_heavy_masses_are_generated_by_phi(self):
        self.assertEqual(-17 + 7 + 10, 0)
        self.assertEqual(-17 - 6 + 23, 0)
        self.assertEqual(+17 - 26 + 9, 0)
        self.assertTrue(all(total % 17 == 0 for total in (7 + 10, -6 + 23, -26 + 9)))

    def test_bounded_minimality_is_scoped_and_reproducible(self):
        self.assertEqual(uv.completion_solutions(25), [])
        solutions = uv.completion_solutions(26)
        self.assertEqual(len(solutions), 8)
        self.assertIn((7, 10, -6, 23, -26, 9), solutions)


class AccidentalSymmetryAndClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frontier = uv.operator_frontier(16)

    def test_no_renormalizable_pq_or_vector_breaker_even_in_overcatalogue(self):
        audit = uv.renormalizable_accidental_symmetry_audit()
        self.assertEqual(audit["pq_or_vector_breaking_candidates"], [])

    def test_no_closure_through_p12(self):
        self.assertIsNone(uv.minimum_vacuum_closure(self.frontier, 12))

    def test_first_necessary_condition_target_is_p13(self):
        closure = uv.minimum_vacuum_closure(self.frontier, 13)
        self.assertIsNotNone(closure)
        self.assertEqual((closure.planck_power, closure.pq, closure.vector), (13, -68, uv.ZERO_VECTOR))

    def test_explicit_p13_certificate_saturates_search(self):
        closure = uv.explicit_p13_certificate()
        labels = Counter(op.label for op in closure.operators)
        self.assertEqual(sorted(labels.values()), [1, 2, 2])
        self.assertEqual((closure.planck_power, closure.pq, closure.vector), (13, -68, uv.ZERO_VECTOR))
        self.assertTrue(all(op.x == 0 and op.centre % 4 == 0 for op in closure.operators))

    def test_explicit_spin10_contraction_is_nonzero(self):
        tensors = np.asarray(spin10.chiral_vector_bilinears(+1))
        gram = np.einsum("aij,bij->ab", tensors.conj(), tensors)
        np.testing.assert_array_equal(np.real_if_close(gram).astype(int), 16 * np.eye(10, dtype=int))


class MixingAndRunningTests(unittest.TestCase):
    def test_exact_axion_projection(self):
        result = uv.axion_mixing(6.313855e11, 1.0e17)
        gauge = np.asarray(result["gauge_direction_in_(aPhi,aS)"])
        physical = np.asarray(result["physical_axion_direction_in_(aPhi,aS)"])
        self.assertAlmostEqual(float(np.dot(gauge / np.linalg.norm(gauge), physical)), 0.0, places=14)
        self.assertLess(abs(result["relative_correction_to_vS_over_17"]), 1.2e-12)

    def test_u1_landau_pole_constraint(self):
        result = uv.abelian_beta_and_landau_bound(1.0e17)
        self.assertEqual(result["b_X_one_loop"], 4919.0)
        self.assertGreater(result["example_landau_pole_GeV"], result["cutoff_GeV"])
        self.assertTrue(0.070 < result["maximum_gX_for_landau_pole_above_cutoff"] < 0.071)


if __name__ == "__main__":
    unittest.main(verbosity=2)
